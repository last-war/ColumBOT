import enum

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, func, Boolean, Text, Table, Enum, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


