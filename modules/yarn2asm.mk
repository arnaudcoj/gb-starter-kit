ifndef MODULES_YARN2ASM
MODULES_YARN2ASM = 1

# OBJS+=$(OBJDIR)/yarn2asm/yarn-runner.o
# $(OBJDIR)/yarn2asm/yarn-runner.o:

$(OBJDIR)/yarn2asm/%.o:modules/yarn2asm/%.asm include/hardware.inc
	$(call $(MKDIR),$(dir $@))
	$(RGBASM) $(ASFLAGS) -Imodules/yarn2asm/ -o $@ $<

modules/yarn2asm/yarn2asm.py:modules/yarn2asm/shunting_yard.py

.SECONDEXPANSION:
$(SRCDIR)/%.yarn.asm:$(SRCDIR)/%.yarn $$(wildcard $(SRCDIR)/%.yarn.meta)
	python modules/yarn2asm/yarn2asm.py $(call $(CAT),$<.meta) $< $@

$(OBJDIR)/%.yarn.o:$(SRCDIR)/%.yarn.asm modules/yarn2asm/yarn.inc include/charmap.inc modules/yarn2asm/yarn2asm.py
	$(call $(MKDIR),$(dir $@))
	$(RGBASM) $(ASFLAGS) -Imodules/yarn2asm/ -Pinclude/charmap.inc -o $@ $<


endif