import juniper


def run_standalone(dialog_class, title=None, position=None):
    """Runs a juniper tool as a standalone dialog
    :param <class:dialog_class> Dialog class of the tool, inherits QWidget
    :param [<str:title>] Title of the dialog
    :return <QDialog:dialog> The created dialog, contains the child tool widget nested inside
    """
    import juniper.widgets as qt_utils

    program_context = juniper.program_context

    if(program_context in ("python",)):
        app = qt_utils.get_application()
        dialog = qt_utils.create_dialog(dialog_class, title=title)
        dialog.show()
        app.exec_()
    else:
        dialog = qt_utils.create_dialog(dialog_class, title=title)
        dialog.show()

    if(position):
        dialog.setGeometry(
            position[0],
            position[1],
            dialog.frameGeometry().width(),
            dialog.frameGeometry().height()
        )

    return dialog
