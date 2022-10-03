/*
:type script
:callbacks [post_startup]
:desc This is a hacky workaround to adding in a Qt based menu on Max startup
:desc it seems like the security changes now remove any python/maxscript menus added during the base startup initialization
:desc this defers it until post startup via a maxscript timer which is hit off a instantly after the whole startup
:desc process is complete.
:supported_hosts [max]
*/
global forceMenuRollout
qtmax = python.import "qtmax"
toolbar = (qtmax.GetQMaxMainWindow()).menuBar()
for i in g_juniperMenus do
(
    toolbar.addMenu(i)
)