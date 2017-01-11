import javax.imageio.ImageIO

/**
 * Screenshot your phone from adb command and pull it into the local folder.
 * if there is only one device in your pc, just capture the screen directly without any choice, else,
 * you need to choose the number of the device that you want to to capture a screen.
 *
 * Usage: groovy phonescreencap.groovy
 * Created by leiweibo on 1/11/17.
 */

def command = 'adb devices'
def proc = command.execute()
def deviceResultLines = proc.in.readLines()

def deviceLinesCount = deviceResultLines.size()
def deviceCount = deviceLinesCount - 2


println "${deviceCount} device(s)"
if (deviceCount == 0) {
    println 'no deviceResultLines attached, please check your phone.'
} else {
    if (deviceCount > 1) {
        deviceResultLines.eachWithIndex {val, idx ->
            if(idx > 0 && idx < deviceLinesCount - 1) {
                println "[${idx}]: ${val}"
            }
        }

        System.in.withReader {
            print "Please input the device no. in above list:"
            def num = it.readLine()
            Range range = new IntRange(1, deviceCount);
            while(!num.isNumber() || !range.contains(num as int)) {
                println "Your input is incorrect, please input a number. or right device number!"
                print "Please input the device no. in above list:"
                num = it.readLine()
            }
            def selectedDeviceLine = deviceResultLines.get(num as int);

            def selectdDevice = selectedDeviceLine.split("\\s")
            doCaptureScreen("-s ${selectdDevice[0]}")
        }
    } else {
        doCaptureScreen("");
    }
}

/**
 * Retry for 2 times.
 * @param deviceStr the command of specify device, eg. "-s device1"
 */
def doCaptureScreen(deviceStr) {
    def retry = 0
    def MAXRETRYCOUNT = 2
    while(!(captureScreen(deviceStr)) && retry ++ < MAXRETRYCOUNT) {
        println "retry for ${retry} time...."
    }
}

/**
 * Real capture screen operation.
 * @param deviceStr the specify command.
 * @return true if capture screen successfully, false if captreu screen failed.
 */
def captureScreen(deviceStr) {
    def targetImg = '/sdcard/screen.png'
    def imgName = 'screen.png'
    def command = "adb ${deviceStr} shell screencap -p $targetImg"
    def proc = command.execute()
    proc.waitFor()

    printlnError(proc)
    if (proc.exitValue() > 0) {
        return false
    }

    command = "adb ${deviceStr} pull $targetImg"
    proc = command.execute()
    proc.waitFor()

    printlnError(proc)
    if (proc.exitValue() > 0) {
        return false
    }

    command = "adb ${deviceStr} shell am rm $targetImg" //删除图片
    proc = command.execute()
    proc.waitFor()
    printlnError(proc)
    if (proc.exitValue() > 0) {
        return false
    }

    command = "open ${imgName}" //删除图片
    command.execute()

    def img = ImageIO.read(new File(imgName));
    println ("The width:${img.width}, the height:${img.height}")

    return true
}

def printlnError(process) {
    if (process.exitValue() > 0 ) {
        println "Std Err: ${process.err.text}"
    }
}