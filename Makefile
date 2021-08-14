PROTO_FN=ttop
PROTO_IDIR=langg/proto
PROTO_ODIR=langg/proto

PROTO_PB_FILE=$(PROTO_IDIR)/$(PROTO_FN).proto
PROTO_PY_FILE=$(PROTO_ODIR)/$(PROTO_FN)_pb2.py

protobuf:
ifeq ("$(wildcard $(PROTO_PY_FILE))", "")
	protoc -I=$(PROTO_IDIR) --python_out=$(PROTO_ODIR) $(PROTO_PB_FILE)
endif

all-letters-format-testing: fn=all-letters-format-testing
all-letters-format-testing: generate

corncob: fn=corncob_lowercase
corncob: generate

# make generate fn=<name-of-/dicts-file-no-ext>
generate: protobuf
	python -m langg \
		--infile dicts/$(fn).txt \
		generate \
		--json-outfile out/$(fn).json \
		--dot-outfile out/$(fn).dot \
		--proto-outfile out/$(fn).proto

.PHONY: clean-all clean-cache clean-proto

clean-cache:
	find langg -type d -name __pycache__ -exec rm -r {} +

clean-proto:
	rm $(PROTO_PY_FILE)

clean-all: clean-cache clean-proto
	rm -rf out && mkdir out
