cd pb
./change_charset.sh
cd ..
python3 split_pb.py
cd pb_out
./generate_java_by_pb.sh
cd ..
python3 generate_java.py

echo '处理完成'