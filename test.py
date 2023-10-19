import collections
import socket
from multiprocessing.managers import SharedMemoryManager
from typing import Self


class SharedListWrapper:
    
    manager = SharedMemoryManager()

    manager.start()

    index = manager.SharedMemory(size=2)
    index.buf[0] = 0
    index.buf[1] = 2
    
    list = manager.ShareableList(range(index.buf[1]))
    
    def resizeList():
        newList = Self.manager.ShareableList(range(Self.index.buf[1] * 2))
        for i in range(Self.index.buf[1]):
            newList[i] = list[i]
        Self.index.buf[1] = Self.index.buf[1] * 2
        return newList

    def addList(value):
        list[Self.index.buf[0]] = value
        Self.index.buf[0] = Self.index.buf[0] + 1
        if(Self.index.buf[0] >= Self.index.buf[1]):
            Self.list = Self.resizeList()
    
    def removeList(value):
        return
        