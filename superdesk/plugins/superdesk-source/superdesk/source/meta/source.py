'''
Created on May 2, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for source API.
'''

from ..api.source import Source
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.mapper import reconstructor
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Boolean
from superdesk.meta.metadata_superdesk import Base
from superdesk.source.meta.type import SourceTypeMapped

# --------------------------------------------------------------------

class SourceMapped(Base, Source):
    '''
    Provides the mapping for Source.
    '''
    __tablename__ = 'source'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Name = Column('name', String(255), nullable=False)
    URI = Column('uri', String(255), nullable=False)
    IsModifiable = Column('modifiable', Boolean, nullable=False)
    # None REST model attribute --------------------------------------
    typeId = Column('fk_type_id', ForeignKey(SourceTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(SourceTypeMapped, backref=backref('parent', uselist=False))

    @reconstructor
    def init_on_load(self):
        self.Type = self.type.Key