cd pb
./change_charset.sh
cd ..
python3 split_pb.py
cd pb_out
./generate_java_by_pb.sh
cd ..
python3 generate_java.py

cd pb_java
# 以下的地址临时写死
cp -r com/* /Users/weibolei/Dev/nb-workspace/trade-tcp-http/biz/manager/src/main/java/com
cd ../java_out
cp -r convert/* /Users/weibolei/Dev/nb-workspace/trade-tcp-http/biz/manager/src/main/java/com/niubang/trade/tth/biz/manager/convert

cp -r models/* /Users/weibolei/Dev/nb-workspace/trade-tcp-http/share/model/src/main/java/com/niubang/trade/tth/share/model

echo '处理完成'