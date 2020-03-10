iconv -f GBK -t utf-8 CrhTxTradeQryPacket.proto > output/CrhTxTradeQryPacket.proto
iconv -f GBK -t utf-8 CrhTxTradeLoginPacket.proto > output/CrhTxTradeLoginPacket.proto
iconv -f GBK -t utf-8 CrhTxTradeBizPacket.proto > output/CrhTxTradeBizPacket.proto
iconv -f GBK -t utf-8 CrhTxTradeBaseDefine.proto > output/CrhTxTradeBaseDefine.proto
iconv -f GBK -t utf-8 CrhTxTradeBankBizPacket.proto > output/CrhTxTradeBankBizPacket.proto
iconv -f GBK -t utf-8 CrhTxTradeApplyBizPacket.proto > output/CrhTxTradeApplyBizPacket.proto


cd pb_out目录
protoc --proto_path=./ --java_out=../pb_java tradeapplybiz/*.proto
protoc --proto_path=./ --java_out=../pb_java tradebankbiz/*.proto 
protoc --proto_path=./ --java_out=../pb_java tradebasedefine/*.proto
protoc --proto_path=./ --java_out=../pb_java tradebiz/*.proto       
protoc --proto_path=./ --java_out=../pb_java tradelogin/*.proto
protoc --proto_path=./ --java_out=../pb_java tradequery/*.proto