from datetime import datetime
from typing import Annotated

from sqlalchemy import Column, Integer, BigInteger, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

created_at_pk = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at_pk = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                  onupdate=text("TIMEZONE('utc', now())"))]


class Deal(Base):
    __tablename__ = 'deals'

    id = Column(BigInteger, primary_key=True)
    deal_id = Column(Integer, nullable=False)
    data = Column(Text)

    created_at: Mapped[created_at_pk]
    updated_at: Mapped[updated_at_pk]
