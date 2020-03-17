protoc_path="~/Dev/dev-tools/protoc-3.0.0-osx-x86_64/bin" # 这个需要自己设置一下
export PATH=$protoc_path
protoc  --proto_path=./ --java_out=../pb_java tradeapplybiz/*.proto
protoc  --proto_path=./ --java_out=../pb_java tradebankbiz/*.proto
protoc  --proto_path=./ --java_out=../pb_java tradebasedefine/*.proto
protoc  --proto_path=./ --java_out=../pb_java tradebiz/*.proto
protoc  --proto_path=./ --java_out=../pb_java tradelogin/*.proto
protoc  --proto_path=./ --java_out=../pb_java tradequery/*.proto
