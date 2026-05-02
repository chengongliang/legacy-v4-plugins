import QtQuick
import Quickshell
import qs.Widgets
import qs.Commons

NIconButtonHot {
    property ShellScreen screen
    property var pluginApi: null

    readonly property var main: pluginApi?.mainInstance ?? ({})
    readonly property real connectedCount: main.connectedCount ?? 0
    readonly property bool isLoading: main.isLoading ?? false
    readonly property var pluginSettings: pluginApi?.pluginSettings ?? ({})
    readonly property string connectedColor: pluginSettings.connectedColor
    readonly property string disconnectedColor: pluginSettings.disconnectedColor

    icon: isLoading ? "reload" : connectedCount > 0 ? "shield-lock" : "shield"
    tooltipText: connectedCount > 0
        ? pluginApi?.tr("common.connected")
        : pluginApi?.tr("common.disconnected")

    colorFg: Color.resolveColorKeyOptional(connectedCount > 0 ? connectedColor : disconnectedColor) ?? Color.mPrimary

    onClicked: pluginApi?.togglePanel(screen, this)
}