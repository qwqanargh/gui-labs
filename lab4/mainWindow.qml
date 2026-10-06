
import QtQuick 2.0
import QtQuick.Window 2.3

import "."

Window {
    id: root
    visible: true
    width: 1000
    height: 800
    title: "Paint!"
    color: "#454545"


    Rectangle {
        anchors.fill: parent
        color: "#454545"
    }

    Rectangle {
        id: tools
        width: parent.width
        height: 150
        color: "#545454"

        property color paintColor: "#33B5E5"
        property int thickness: 1
        property int spacing: 4

        Column {
            spacing: tools.spacing
            anchors.centerIn: parent
            anchors.horizontalCenterOffset: -110   

            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444"]
                    Square {
                        active: tools.paintColor === color
                        color: modelData
                        onClicked: tools.paintColor = color
                    }
                }
            }

            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: [1,2,3,4,5]

                    Circle {
                        id: circle
                        active: tools.thickness === thickness
                        thickness: modelData
                        text: thickness
                        onClicked: tools.thickness = thickness
                    }
                }
            }
        }

  
        Column {
            anchors.right: parent.right
            anchors.rightMargin: 14
            anchors.verticalCenter: parent.verticalCenter
            width: 270
            spacing: 4

            Text {
                width: parent.width
                color: "white"
                font.pixelSize: 15
                font.bold: true
                text: _backend.autosave ? "Автосохранение каждые " + _backend.interval + " с"
                                        : "Автосохранение выключено"
            }
            Text {
                width: parent.width
                color: "#dddddd"
                font.pixelSize: 13
                text: "Сохранено файлов: " + _backend.savedCount
            }
            Text {
                width: parent.width
                color: "#dddddd"
                font.pixelSize: 13
                elide: Text.ElideMiddle
                text: "Последний: " + (_backend.lastSaved !== "" ? _backend.lastSaved : "—")
            }
            Text {
                width: parent.width
                color: "#dddddd"
                font.pixelSize: 13
                elide: Text.ElideMiddle
                text: "Папка: " + _backend.saveDir
            }
            Text {
                width: parent.width
                color: _backend.dirty ? "#FFBB33" : "#99CC00"
                font.pixelSize: 13
                text: _backend.dirty ? "● есть несохранённые изменения" : "● всё сохранено"
            }
        }

    }

    
    Rectangle {
        id: savePanel
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        height: 50
        color: "#454545"

  
    Rectangle {
        anchors.fill: parent
        color: "#454545"
    }
        Row {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
            spacing: 8

            TextButton {
                text: _backend.autosave ? "Автосохранение: ВКЛ" : "Автосохранение: ВЫКЛ"
                checked: _backend.autosave
                onClicked: _backend.toggleAutosave()
            }
            TextButton { text: "−"; width: 30; onClicked: _backend.changeInterval(-1) }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "каждые " + _backend.interval + " с"
                color: "white"
                font.pixelSize: 14
                width: 90
                horizontalAlignment: Text.AlignHCenter
            }
            TextButton { text: "+"; width: 30; onClicked: _backend.changeInterval(1) }
            TextButton { text: "Сохранить сейчас"; onClicked: _backend.saveNow() }
            TextButton { text: "Папка…"; onClicked: _backend.chooseFolder() }
            TextButton { text: "Очистить"; onClicked: canvas.clear() }
        }

    }

    Canvas {
        id: canvas
        objectName: "canvas"   // по этому имени backend находит холст
        anchors {
            left: parent.left
            right: parent.right
            top: tools.bottom
            bottom: savePanel.top
            margins: 8
        }

        property real lastX
        property real lastY
        property color color: tools.paintColor
        property bool needClear: true   
        property var pending: []       

        function clear() {
            needClear = true
            requestPaint()
            _backend.markDirty()   
        }

        onPaint: {
            var ctx = getContext("2d")
            if (needClear) {
                
                ctx.fillStyle = "white"
                ctx.fillRect(0, 0, width, height)
                needClear = false
                return
            }
            if (pending.length === 0)   
                return
            ctx.lineWidth = tools.thickness
            ctx.strokeStyle = canvas.color
            ctx.lineCap = "round"
            ctx.lineJoin = "round"
            ctx.beginPath()
            ctx.moveTo(lastX, lastY)
            
            for (var i = 0; i < pending.length; i++) {
                lastX = pending[i].x
                lastY = pending[i].y
                ctx.lineTo(lastX, lastY)
            }
            pending = []
            ctx.stroke()
            _backend.markDirty()   
        }

        MouseArea {
            id: paint_area
            anchors.fill: parent

            onPressed: {
                canvas.lastX = mouseX
                canvas.lastY = mouseY
            }

            onPositionChanged: {
                canvas.pending.push(Qt.point(mouseX, mouseY))
                canvas.requestPaint()
            }
        }
    }
}
