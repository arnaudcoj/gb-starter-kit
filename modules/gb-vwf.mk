ifndef MODULES_GB-VWF
MODULES_GB-VWF = 1

$(INCDIR)/charmap.inc:modules/gb-vwf/vwf.asm
	$(call $(MKDIR),$(INCDIR))
	$(RGBASM) $(ASFLAGS) -DPRINT_CHARMAP $^ > $@

VWFENCODER:= modules/gb-vwf/target/release/font_encoder$(EXE)

# TODO ask to install rust and gcc/mingw if needed
modules/gb-vwf/target/release/font_encoder$(EXE):modules/gb-vwf/font_encoder/Cargo.toml
	cargo build --release --manifest-path=$^

assets/%.vwf:$(SRCDIR)/assets/%.png $(VWFENCODER)
	$(call $(MKDIR),$(dir $@))
	$(VWFENCODER) $< $@

assets/%.vwflen:$(SRCDIR)/assets/%.png $(VWFENCODER)
	$(call $(MKDIR),$(dir $@))
	$(VWFENCODER) $< $(@:.vwflen=.vwf)

include $(VWF_CFG_FILE:.inc=.mk)
OBJS+=$(OBJDIR)/gb-vwf/vwf.o

$(OBJDIR)/gb-vwf/vwf.o: modules/gb-vwf/vwf.asm $(VWF_CFG_FILE) $(VWF_CFG_FILE:.inc=.mk)
	$(call $(MKDIR),$(dir $@))
	$(RGBASM) $(ASFLAGS) -Imodules/gb-vwf/ -o $@ $<
	
endif
