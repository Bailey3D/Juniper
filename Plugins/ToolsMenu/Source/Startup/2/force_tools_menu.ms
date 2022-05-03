/*
:script
:type startup
:desc This is a hacky workaround to adding in a Qt based menu on Max startup
:desc it seems like the security changes now remove any python/maxscript menus added during the base startup initialization
:desc this defers it until post startup via a maxscript timer which is hit off a instantly after the whole startup
:desc process is complete.
*/
(
    global forceMenuRollout
    updatesCount = 0

    rollout forceMenuRollout "forceMenuRollout"
    (
        timer updateTimer active:on interval:1

        on updateTimer tick do
        (
            if(updatesCount == 1) do
            (
                updateTimer.active = off
                destroyDialog forceMenuRollout

                qtmax = python.import "qtmax"
                toolbar = (qtmax.GetQMaxMainWindow()).menuBar()
                for i in g_juniperMenus do
                (
                    toolbar.addMenu(i)
                )
            )
            updatesCount += 1
        )
    )

    createDialog forceMenuRollout
)