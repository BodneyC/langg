PROTO_IDIR=langg/proto
PROTO_ODIR=langg/proto
PROTO_SRC=ttop.proto

protobuf:
	protoc -I=$(PROTO_IDIR) --python_out=$(PROTO_ODIR) $(PROTO_IDIR)/$(PROTO_SRC)
