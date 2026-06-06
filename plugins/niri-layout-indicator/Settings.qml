import QtQuick
import QtQuick.Layouts
import Quickshell
import qs.Commons
import qs.Widgets
import qs.Services.UI

Item {
  id: rootItem

  implicitWidth: 600
  implicitHeight: root.implicitHeight
  width: Math.max(implicitWidth, parent ? parent.width : 0)

  property var pluginApi: null
  ColumnLayout {
    id: root

    implicitWidth: 600
    width: parent.width
    spacing: Style.marginM

    property var cfg: rootItem.pluginApi?.pluginSettings || ({})
    property var defaults: rootItem.pluginApi?.manifest?.metadata?.defaultSettings || ({})

    property string editDisplayMode: cfg.displayMode || defaults.displayMode || "text"
    property string editMiddleClickAction: cfg.middleClickAction || defaults.middleClickAction || "previous"
    property int editPollIntervalMs: cfg.pollIntervalMs ?? defaults.pollIntervalMs ?? 750

    function tr(key) {
      return rootItem.pluginApi?.tr(key)
    }

    function saveSettings() {
      if (!rootItem.pluginApi)
        return

      rootItem.pluginApi.pluginSettings.displayMode = root.editDisplayMode
      rootItem.pluginApi.pluginSettings.middleClickAction = root.editMiddleClickAction
      rootItem.pluginApi.pluginSettings.pollIntervalMs = root.editPollIntervalMs
      rootItem.pluginApi.saveSettings()
    }
    NText {
      Layout.fillWidth: true
      text: root.tr("settings.title")
      pointSize: Style.fontSizeXXL
      font.weight: Style.fontWeightBold
      color: Color.mOnSurface
    }

    NText {
      Layout.fillWidth: true
      text: root.tr("settings.description")
      color: Color.mOnSurfaceVariant
      pointSize: Style.fontSizeM
      wrapMode: Text.WordWrap
    }

    NBox {
      Layout.fillWidth: true
      Layout.preferredHeight: displayContent.implicitHeight + Style.marginM * 2
      color: Color.mSurfaceVariant

      ColumnLayout {
        id: displayContent
        anchors.fill: parent
        anchors.margins: Style.marginM
        spacing: Style.marginS

        NText {
          Layout.fillWidth: true
          text: root.tr("settings.display.title")
          pointSize: Style.fontSizeL
          font.weight: Style.fontWeightBold
          color: Color.mOnSurface
        }

        NText {
          Layout.fillWidth: true
          text: root.tr("settings.display.description")
          color: Color.mOnSurfaceVariant
          pointSize: Style.fontSizeS
          wrapMode: Text.WordWrap
        }

        NComboBox {
          id: displayCombo

          Layout.preferredWidth: 240 * Style.uiScaleRatio
          Layout.preferredHeight: Style.baseWidgetSize

          model: ListModel {
            ListElement { name: "Text: en, ru"; key: "text" }
            ListElement { name: "Flag: 🇺🇸, 🇷🇺"; key: "flag" }
          }

          currentKey: root.editDisplayMode

          onSelected: key => {
            root.editDisplayMode = key
          }
        }
      }
    }

    NBox {
      Layout.fillWidth: true
      Layout.preferredHeight: middleContent.implicitHeight + Style.marginM * 2
      color: Color.mSurfaceVariant

      ColumnLayout {
        id: middleContent
        anchors.fill: parent
        anchors.margins: Style.marginM
        spacing: Style.marginS

        NText {
          Layout.fillWidth: true
          text: root.tr("settings.middle.title")
          pointSize: Style.fontSizeL
          font.weight: Style.fontWeightBold
          color: Color.mOnSurface
        }

        NText {
          Layout.fillWidth: true
          text: root.tr("settings.middle.description")
          color: Color.mOnSurfaceVariant
          pointSize: Style.fontSizeS
          wrapMode: Text.WordWrap
        }

        NComboBox {
          id: middleCombo

          Layout.preferredWidth: 260 * Style.uiScaleRatio
          Layout.preferredHeight: Style.baseWidgetSize

          model: ListModel {
            ListElement { name: "Previous layout"; key: "previous" }
            ListElement { name: "Toggle display mode"; key: "toggle-mode" }
          }

          currentKey: root.editMiddleClickAction

          onSelected: key => {
            root.editMiddleClickAction = key
          }
        }
      }
    }

    NBox {
      Layout.fillWidth: true
      Layout.preferredHeight: updateContent.implicitHeight + Style.marginM * 2
      color: Color.mSurfaceVariant

      ColumnLayout {
        id: updateContent
        anchors.fill: parent
        anchors.margins: Style.marginM
        spacing: Style.marginS

        NText {
          Layout.fillWidth: true
          text: root.tr("settings.update.title")
          pointSize: Style.fontSizeL
          font.weight: Style.fontWeightBold
          color: Color.mOnSurface
        }

        NText {
          Layout.fillWidth: true
          text: root.tr("settings.update.description")
          color: Color.mOnSurfaceVariant
          pointSize: Style.fontSizeS
          wrapMode: Text.WordWrap
        }

        NComboBox {
          id: pollCombo

          Layout.preferredWidth: 180 * Style.uiScaleRatio
          Layout.preferredHeight: Style.baseWidgetSize

          model: ListModel {
            ListElement { name: "250 ms"; key: "250" }
            ListElement { name: "500 ms"; key: "500" }
            ListElement { name: "750 ms"; key: "750" }
            ListElement { name: "1000 ms"; key: "1000" }
            ListElement { name: "1500 ms"; key: "1500" }
          }

          currentKey: root.editPollIntervalMs.toString()

          onSelected: key => {
            root.editPollIntervalMs = parseInt(key)
          }
        }
      }
    }

    Item {
      Layout.fillHeight: true
    }
  }

  Connections {
    target: rootItem.pluginApi

    function onSaveRequested() {
      root.saveSettings()
    }
  }
}
