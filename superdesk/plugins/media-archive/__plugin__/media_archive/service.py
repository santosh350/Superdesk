'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media archive superdesk.
'''

from ..superdesk import service
from ..superdesk.db_superdesk import bindSuperdeskSession, createTables
from ally.container import ioc, support
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from superdesk.media_archive.api.meta_data import IMetaDataService,\
    IMetaDataUploadService
from superdesk.media_archive.core.impl.thumbnail_manager import ThumbnailManager, \
    ThumbnailCreatorGraphicsMagick
from superdesk.media_archive.core.spec import IThumbnailManager, \
    IThumbnailCreator, QueryIndexer
from superdesk.media_archive.impl.meta_data import IMetaDataHandler, \
    MetaDataServiceAlchemy
import logging
from superdesk.media_archive.core.impl.query_service_creator import createService
from ..plugin.registry import registerService
from superdesk.media_archive.impl.query_criteria import QueryCriteriaService
from superdesk.media_archive.api.query_criteria import IQueryCriteriaService
from cdm.impl.local_filesystem import LocalFileSystemCDM, IDelivery,\
    HTTPDelivery
from __plugin__.cdm.local_cdm import server_uri, repository_path

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def addMetaDataHandler(handler):
    if not isinstance(handler, IMetaDataService): metaDataHandlers().append(handler)

support.wireEntities(ThumbnailManager, ThumbnailCreatorGraphicsMagick)
support.bindToEntities(ThumbnailManager, binders=bindSuperdeskSession)
support.listenToEntities(IMetaDataHandler, listeners=addMetaDataHandler, setupModule=service, beforeBinding=False)

# --------------------------------------------------------------------
    
@ioc.config
def thumbnail_sizes():
    '''
    Contains the thumbnail sizes available for the media archive.
    This is basically just a simple dictionary{string, tuple(integer, integer)} that has as a key a path safe name
    and as a value a tuple with the width/height of the thumbnail.
    example: {'small': [100, 100]}
    '''
    return { 'tiny' : [16, 16], 'small' : [32, 32], 'medium' : [64, 64], 'large' : [128, 128], 'huge' : [256, 256] }

# --------------------------------------------------------------------

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.entity
def cdmThumbnail() -> ICDM:
    '''
    The content delivery manager (CDM) for the thumbnails media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/thumbnail/%s')

# --------------------------------------------------------------------

@ioc.entity
def thumbnailManager() -> IThumbnailManager:
    b = ThumbnailManager()
    b.thumbnailSizes = thumbnail_sizes()
    b.thumbnailCreator = thumbnailCreator()
    b.cdm = cdmThumbnail()
    return b

# --------------------------------------------------------------------

@ioc.entity
def thumbnailCreator() -> IThumbnailCreator:
    c = ThumbnailCreatorGraphicsMagick()
    return c

# --------------------------------------------------------------------

@ioc.replace(ioc.getEntity(IMetaDataUploadService, service))
def metaDataService() -> IMetaDataUploadService:
    b = MetaDataServiceAlchemy()
    b.cdmArchive = cdmArchive()
    b.metaDataHandlers = metaDataHandlers()
    return b

# --------------------------------------------------------------------

@ioc.entity
def metaDataHandlers(): return []

# --------------------------------------------------------------------

@ioc.entity
def queryIndexer() -> QueryIndexer:
    b = QueryIndexer()
    return b

# --------------------------------------------------------------------

@ioc.after(createTables)
def publishQueryService():
    b = createService(queryIndexer())
    registerService(b, (bindSuperdeskSession, ))
    
# --------------------------------------------------------------------

@ioc.replace(ioc.getEntity(IQueryCriteriaService, service))
def publishQueryCriteriaService() -> IQueryCriteriaService:
    b = QueryCriteriaService(queryIndexer() )
    return b    
    
# --------------------------------------------------------------------

@ioc.after(createTables)
def deploy():
    metaDataService().deploy()


