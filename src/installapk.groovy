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

    printlnError(proc)
}

def printlnError(process) {
    if (process.exitValue() > 0 ) {
        println "Std Err: ${process.err.text}"
    }
}
