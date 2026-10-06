import QtQuick 2.0


Rectangle {
    id: root

    property string text: ""
    property bool checked: false
    signal clicked

    width: label.implicitWidth + 24
    height: 30
    radius: 6
    color: area.pressed ? "#2a2a2a" : (checked ? "#33B5E5" : (area.containsMouse ? "#6a6a6a" : "#5e5e5e"))
    border.color: "#7a7a7a"

    Text {
        id: label
        anchors.centerIn: parent
        text: root.text
        color: "white"
        font.pixelSize: 14
    }

    MouseArea {
        id: area
        anchors.fill: parent
        hoverEnabled: true
        onClicked: root.clicked()
    }
}
