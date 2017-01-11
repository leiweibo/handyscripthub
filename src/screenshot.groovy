/**
 * Screenshot your phone from adb command.
 * Created by leiweibo on 1/11/17.
 */

def targetImg = '/sdcard/screen.png'
def command = "adb shell screencap -p $targetImg"
def proc = command.execute()
proc.waitFor()

println "Process exit code: ${proc.exitValue()}"
println "Std Err: ${proc.err.text}"
println "Std Out: ${proc.in.text}"

command = "adb pull $targetImg"
proc = command.execute()
proc.waitFor()
println('pull image success.')

command = "adb shell am rm $targetImg" //删除图片
command.execute()

command = "open ." //删除图片
command.execute()
