'''
Created on Mar 6, 2012

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

@author: Mihai Balaceanu
'''
from superdesk.user.api.user import IUserService
from ally.container.ioc import injected
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.user.meta.user import User, QUser
from platform import python_version

# --------------------------------------------------------------------

@injected
class UserServiceAlchemy(EntityServiceAlchemy, IUserService):
    '''
    @see: IUserService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, User, QUser)
