from __future__ import absolute_import

import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from data.db import Base


class Cart(Base):

    __tablename__ = 'cart'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)

    items = relationship('Item', back_populates='cart')


class Item(Base):

    __tablename__ = 'item'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUIDType, ForeignKey('cart.id'))
    external_id = Column(String, nullable=False)
    name = Column(String)
    value = Column(Integer)

    cart = relationship('Cart', back_populates='items')

    __table_args__ = (
        UniqueConstraint('cart_id', 'external_id', name='_cart_uc'),
    )
