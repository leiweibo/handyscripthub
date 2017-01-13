/**
 * Created by leiweibo on 1/13/17.
 */

def apkPath = "./app.apk"
System.in.withReader {
    print "Please input the apk apkPath:"
    apkPath = it.readLine()
    def apkFile = new File(apkPath)
    while (!apkFile.exists()) {
        print "Please re-input the correct apk apkPath:"
        apkPath = it.readLine()
        apkFile = new File(apkPath)
    }
}
println "the apkPath is ${apkPath}"

def command = 'adb devices'
def proc = command.execute()
def deviceResultLines = proc.in.readLines()

def deviceLinesCount = deviceResultLines.size()
def deviceCount = deviceLinesCount - 2

if (deviceCount == 0) {
    println 'no device attached, please check your phone.'
} else {
    deviceResultLines.eachWithIndex { val, idx ->
        if(idx > 0 && idx < deviceLinesCount - 1) {
            def deviceStr = val.split("\\s")
            println deviceStr
            installApk("-s ${deviceStr[0]}", apkPath)
        }
    }
}

def installApk(deviceStr, apkPath) {
    def command = "adb ${deviceStr} install -r $apkPath"
    println command
    def proc = command.execute()
    proc.waitFor()

    command = "aapt dump badging ${apkPath} | grep launchable-activity:/ name="

    proc = command.execute()
    proc.waitFor()
    def fetchLaunchActivityResult = proc.in.text.readLines()
    def packageName;
    def launchActivty;
    for (line in fetchLaunchActivityResult) {
        if (line.startsWith("package: name=")) {
            tmpLine = line.split("\\s")[1]
            if (tmpLine) {
                packageName = tmpLine.split("=")[1]
            }
        } else if (line.startsWith("launchable-activity:")) {
            tmpLine = line.split("\\s")[1]
            if (tmpLine) {
                launchActivty = tmpLine.split("=")[1]
            }
        }
    }
    if (packageName == '' || launchActivty == '') {
        println "please check, your package name or launch activity parse incorrect."
        println "packageName: $packageName\nlauchActivity：$launchActivty"
    }
    startApk(deviceStr, proc, packageName, launchActivty)
}

def startApk(deviceStr, process, packageName, activityClazzName) {
    if (process.exitValue() > 0 ) {
        println "Std Err: ${process.err.text}"
    } else {
        def command = "adb ${deviceStr} shell am start -n ${packageName}/${activityClazzName}"
        def proc = command.execute()
        println "Std Err: ${proc.err.text}"
        proc.waitFor()
        println "it's done...."
    }
}
