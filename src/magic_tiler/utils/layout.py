# https://stackoverflow.com/questions/36286894/name-not-defined-in-type-annotation
from __future__ import annotations

import collections
import logging
from typing import Any, Dict, List, Optional, Set

from magic_tiler.utils import dtos
from magic_tiler.utils import interfaces


class TreeNode(object):
    def __init__(self, data: Any, parent: TreeNode = None) -> None:
        self._data = data
        self._children: List[TreeNode] = []
        if parent:
            parent.add_child(self)

    def add_child(self, node: TreeNode) -> None:
        self._children.append(node)

    def get_leftmost_descendant(self) -> TreeNode:
        if self.is_parent:
            return self.children[0].get_leftmost_descendant()
        else:
            return self

    @property
    def is_parent(self) -> bool:
        return len(self._children) > 0

    @property
    def children(self) -> List[TreeNode]:
        return self._children

    @property
    def data(self) -> Any:
        return self._data

    def __str__(self) -> str:
        return f"{self.data}: {self._children}"

    def __repr__(self) -> str:
        return f"TreeNode<{len(self.children)}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TreeNode):
            return False
        if len(self.children) != len(other.children):
            return False
        for my_child, other_child in zip(self.children, other.children):
            if my_child != other_child:
                return False
        return self.data == other.data


def create_tree(node: Dict, parent: Optional[TreeNode] = None) -> TreeNode:
    if "mark" in node:
        current_node = TreeNode(
            dtos.WindowDetails(mark=node["mark"], command=node["command"]),
            parent=parent,
        )
    elif "children" in node:
        current_node = TreeNode(node["split"], parent=parent)
        if len(node["children"]) <= 1:
            raise RuntimeError("each parent needs at least 2 children")
        for child in node["children"]:
            create_tree(child, current_node)
    else:
        raise RuntimeError("invalid config file")
    return current_node


# We use depth-first traversal to create each leaf node in the tree. We
# create the leftmost descendant of each parent first so that it can reserve
# space for its other siblings.


class Layout(object):
    def __init__(
        self,
        config_reader: interfaces.ConfigReader,
        layout_name: str,
        window_manager: interfaces.TilingWindowManager,
    ) -> None:
        self._window_manager = window_manager
        try:
            root_node = config_reader.to_dict()[layout_name]
        except KeyError:
            raise KeyError(f'Could not find layout "{layout_name}" in config')
        if "size" in root_node:
            raise RuntimeError("root node shouldn't have a size. size is implied 100")
        root_node["size"] = 100
        tree = create_tree(root_node)
        self._parse_tree(tree)

    def _parse_tree(self, root_node: TreeNode) -> None:
        node_queue = collections.deque([root_node])
        self._created_windows: Set[str] = set()
        while len(node_queue) >= 1:
            current_node = node_queue.popleft()
            logging.debug(f"dequeuing {current_node}")
            if current_node.is_parent:
                self._attempt_to_create_leftmost_descendant(current_node.children[0])
                self._window_manager.split(current_node.data)
                for child in current_node.children[1:]:
                    self._attempt_to_create_leftmost_descendant(child)
                for child in current_node.children:
                    node_queue.append(child)

    def _attempt_to_create_leftmost_descendant(self, node: TreeNode) -> None:
        logging.debug(f"getting leftmost descendant of {node}")
        leftmost_descendant = node.get_leftmost_descendant()
        if leftmost_descendant.data.mark in self._created_windows:
            self._window_manager.focus(leftmost_descendant.data)
        else:
            self._window_manager.make_window(leftmost_descendant.data)
            self._created_windows.add(leftmost_descendant.data.mark)
