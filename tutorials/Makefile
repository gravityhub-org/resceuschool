# RESCEU GW lensing school tutorials
#
#   make / make bilby     # bilby PE products (default)
#   make cogwheel         # cogwheel PE products
#   make gwfast           # gwfast Fisher-matrix products
#   make millilens        # millilensing PE on unlensed 01 data
#   make millilens-lensed # millilensing PE on a lensed two-image injection
#   make nonlensed-on-lensed  # tutorial-01 PE (unlensed model) on that lensed signal
#   make summarise           # evidences, Bayes factors, shared-parameter overlays
#   make clean / clean-cogwheel / clean-gwfast / clean-millilens / clean-millilens-lensed / clean-nonlensed-on-lensed / clean-summarise / clean-all
#   make force / force-cogwheel / force-gwfast / force-millilens / force-millilens-lensed / force-nonlensed-on-lensed / force-summarise
#
# Products are file targets, so a completed run is a no-op. Interrupted
# sampling runs resume from the sampler checkpoint (same cached injection).
# Editing the script does not rebuild by itself — use `make force*`.
UV ?= uv
# Headless plotting (bilby / matplotlib); override with e.g. MPLBACKEND=TkAgg if needed.
export MPLBACKEND ?= Agg
# Dynesty worker processes per bilby run (override with NPOOL=...).
export NPOOL ?= 8

# --- bilby ---
BILBY_SCRIPT := 01_parameter_estimation.py
BILBY_OUTDIR := output/01_parameter_estimation
BILBY_RUNDIR := $(BILBY_OUTDIR)/bilby_run
BILBY_LABEL := lhvk_distance_demo
BILBY_WAVEFORMS := $(BILBY_OUTDIR)/lhvk_waveforms.png
BILBY_CORNER := $(BILBY_OUTDIR)/posterior_corner.png
BILBY_RESULT := $(BILBY_RUNDIR)/$(BILBY_LABEL)_result.json
BILBY_PRODUCTS := $(BILBY_WAVEFORMS) $(BILBY_CORNER) $(BILBY_RESULT)

# --- cogwheel ---
COGWHEEL_SCRIPT := 01_parameter_estimation_cogwheel.py
COGWHEEL_OUTDIR := output/01_parameter_estimation_cogwheel
COGWHEEL_RUNDIR := $(COGWHEEL_OUTDIR)/cogwheel_run
COGWHEEL_WAVEFORMS := $(COGWHEEL_OUTDIR)/lhvk_waveforms.png
COGWHEEL_CORNER := $(COGWHEEL_OUTDIR)/posterior_corner.png
COGWHEEL_RESULT := $(COGWHEEL_RUNDIR)/samples.feather
COGWHEEL_PRODUCTS := $(COGWHEEL_WAVEFORMS) $(COGWHEEL_CORNER) $(COGWHEEL_RESULT)

# --- gwfast (Fisher matrix) ---
GWFAST_SCRIPT := 01_parameter_estimation_gwfast.py
GWFAST_OUTDIR := output/01_parameter_estimation_gwfast
GWFAST_RUNDIR := $(GWFAST_OUTDIR)/gwfast_run
GWFAST_WAVEFORMS := $(GWFAST_OUTDIR)/lhvk_waveforms.png
GWFAST_CORNER := $(GWFAST_OUTDIR)/posterior_corner.png
GWFAST_RESULT := $(GWFAST_RUNDIR)/fisher_result.json
GWFAST_PRODUCTS := $(GWFAST_WAVEFORMS) $(GWFAST_CORNER) $(GWFAST_RESULT)

# --- millilensing PE on unlensed 01 data ---
MILLENS_SCRIPT := 02_parameter_estimation_millisecondlens_on_unlensed.py
MILLENS_OUTDIR := output/02_parameter_estimation_millisecondlens_on_unlensed
MILLENS_RUNDIR := $(MILLENS_OUTDIR)/bilby_run
MILLENS_LABEL := millilens_on_unlensed
MILLENS_WAVEFORMS := $(MILLENS_OUTDIR)/lhvk_waveforms.png
MILLENS_CORNER := $(MILLENS_OUTDIR)/posterior_corner.png
MILLENS_CORNER_LENS := $(MILLENS_OUTDIR)/posterior_corner_lens.png
MILLENS_N1_PHASE := $(MILLENS_OUTDIR)/n1_vs_phase.png
MILLENS_RESULT := $(MILLENS_RUNDIR)/$(MILLENS_LABEL)_result.json
MILLENS_PRODUCTS := $(MILLENS_WAVEFORMS) $(MILLENS_CORNER) $(MILLENS_CORNER_LENS) \
	$(MILLENS_N1_PHASE) $(MILLENS_RESULT)
# Shared strain cache produced by tutorial 01.
BILBY_IFO_CACHE := $(BILBY_RUNDIR)/injection_ifos.npz

# --- millilensing PE on a lensed two-image injection ---
MILLENS_LENSED_SCRIPT := 03_parameter_estimation_millisecondlens_on_lensed.py
MILLENS_LENSED_OUTDIR := output/03_parameter_estimation_millisecondlens_on_lensed
MILLENS_LENSED_RUNDIR := $(MILLENS_LENSED_OUTDIR)/bilby_run
MILLENS_LENSED_LABEL := millilens_on_lensed
MILLENS_LENSED_WAVEFORMS := $(MILLENS_LENSED_OUTDIR)/lhvk_waveforms.png
MILLENS_LENSED_CORNER := $(MILLENS_LENSED_OUTDIR)/posterior_corner.png
MILLENS_LENSED_CORNER_LENS := $(MILLENS_LENSED_OUTDIR)/posterior_corner_lens.png
MILLENS_LENSED_RESULT := $(MILLENS_LENSED_RUNDIR)/$(MILLENS_LENSED_LABEL)_result.json
MILLENS_LENSED_PRODUCTS := $(MILLENS_LENSED_WAVEFORMS) $(MILLENS_LENSED_CORNER) \
	$(MILLENS_LENSED_CORNER_LENS) $(MILLENS_LENSED_RESULT)
MILLENS_LENSED_IFO_CACHE := $(MILLENS_LENSED_RUNDIR)/injection_ifos.npz

# --- unlensed (tutorial 01) PE on the shared lensed injection ---
NONLENSED_LENSED_SCRIPT := 03_parameter_estimation_nonlensed_on_lensed.py
NONLENSED_LENSED_OUTDIR := output/03_parameter_estimation_nonlensed_on_lensed
NONLENSED_LENSED_RUNDIR := $(NONLENSED_LENSED_OUTDIR)/bilby_run
NONLENSED_LENSED_LABEL := nonlensed_on_lensed
NONLENSED_LENSED_WAVEFORMS := $(NONLENSED_LENSED_OUTDIR)/lhvk_waveforms.png
NONLENSED_LENSED_CORNER := $(NONLENSED_LENSED_OUTDIR)/posterior_corner.png
NONLENSED_LENSED_RESULT := $(NONLENSED_LENSED_RUNDIR)/$(NONLENSED_LENSED_LABEL)_result.json
NONLENSED_LENSED_PRODUCTS := $(NONLENSED_LENSED_WAVEFORMS) $(NONLENSED_LENSED_CORNER) \
	$(NONLENSED_LENSED_RESULT)

# --- summarise 01+02+03 evidences / Bayes factors / overlays ---
SUMMARISE_SCRIPT := 04_summarise_results.py
SUMMARISE_OUTDIR := output/04_summarise_results
SUMMARISE_UNLENSED := $(SUMMARISE_OUTDIR)/comparison_unlensed_injection.png
SUMMARISE_LENSED := $(SUMMARISE_OUTDIR)/comparison_lensed_injection.png
SUMMARISE_PRODUCTS := $(SUMMARISE_UNLENSED) $(SUMMARISE_LENSED)

.PHONY: all bilby cogwheel gwfast millilens millilens-lensed nonlensed-on-lensed \
	summarise clean clean-cogwheel clean-gwfast clean-millilens clean-millilens-lensed \
	clean-nonlensed-on-lensed clean-summarise clean-all force force-cogwheel \
	force-gwfast force-millilens force-millilens-lensed force-nonlensed-on-lensed \
	force-summarise help

all: bilby

bilby: $(BILBY_PRODUCTS)

cogwheel: $(COGWHEEL_PRODUCTS)

gwfast: $(GWFAST_PRODUCTS)

millilens: $(MILLENS_PRODUCTS)

millilens-lensed: $(MILLENS_LENSED_PRODUCTS)

nonlensed-on-lensed: $(NONLENSED_LENSED_PRODUCTS)

summarise: $(SUMMARISE_PRODUCTS)

# Grouped targets (GNU make ≥ 4.3): one recipe, no re-run once products exist.
$(BILBY_PRODUCTS) &:
	$(UV) run python $(BILBY_SCRIPT)
	@test -f $(BILBY_WAVEFORMS)
	@test -f $(BILBY_CORNER)
	@test -f $(BILBY_RESULT)

$(COGWHEEL_PRODUCTS) &:
	$(UV) run python $(COGWHEEL_SCRIPT)
	@test -f $(COGWHEEL_WAVEFORMS)
	@test -f $(COGWHEEL_CORNER)
	@test -f $(COGWHEEL_RESULT)

$(GWFAST_PRODUCTS) &:
	$(UV) run python $(GWFAST_SCRIPT)
	@test -f $(GWFAST_WAVEFORMS)
	@test -f $(GWFAST_CORNER)
	@test -f $(GWFAST_RESULT)

# Needs the shared 01 strain cache; build bilby products first if missing.
$(MILLENS_PRODUCTS) &: $(BILBY_IFO_CACHE)
	$(UV) run python $(MILLENS_SCRIPT)
	@test -f $(MILLENS_WAVEFORMS)
	@test -f $(MILLENS_CORNER)
	@test -f $(MILLENS_CORNER_LENS)
	@test -f $(MILLENS_N1_PHASE)
	@test -f $(MILLENS_RESULT)

$(BILBY_IFO_CACHE):
	@$(MAKE) bilby

$(MILLENS_LENSED_PRODUCTS) &:
	$(UV) run python $(MILLENS_LENSED_SCRIPT)
	@test -f $(MILLENS_LENSED_WAVEFORMS)
	@test -f $(MILLENS_LENSED_CORNER)
	@test -f $(MILLENS_LENSED_CORNER_LENS)
	@test -f $(MILLENS_LENSED_RESULT)

# Shares the millilens-lensed strain cache; script creates it if missing.
$(NONLENSED_LENSED_PRODUCTS) &:
	$(UV) run python $(NONLENSED_LENSED_SCRIPT)
	@test -f $(NONLENSED_LENSED_WAVEFORMS)
	@test -f $(NONLENSED_LENSED_CORNER)
	@test -f $(NONLENSED_LENSED_RESULT)

# Needs all four bilby result JSONs from 01 / 02 / 03m / 03n.
$(SUMMARISE_PRODUCTS) &: $(BILBY_RESULT) $(MILLENS_RESULT) $(MILLENS_LENSED_RESULT) \
	$(NONLENSED_LENSED_RESULT)
	$(UV) run python $(SUMMARISE_SCRIPT)
	@test -f $(SUMMARISE_UNLENSED)
	@test -f $(SUMMARISE_LENSED)

clean:
	rm -rf $(BILBY_OUTDIR)

clean-cogwheel:
	rm -rf $(COGWHEEL_OUTDIR)

clean-gwfast:
	rm -rf $(GWFAST_OUTDIR)

clean-millilens:
	rm -rf $(MILLENS_OUTDIR)

clean-millilens-lensed:
	rm -rf $(MILLENS_LENSED_OUTDIR)

clean-nonlensed-on-lensed:
	rm -rf $(NONLENSED_LENSED_OUTDIR)

clean-summarise:
	rm -rf $(SUMMARISE_OUTDIR)

clean-all: clean clean-cogwheel clean-gwfast clean-millilens clean-millilens-lensed \
	clean-nonlensed-on-lensed clean-summarise

force: clean
	$(MAKE) bilby

force-cogwheel: clean-cogwheel
	$(MAKE) cogwheel

force-gwfast: clean-gwfast
	$(MAKE) gwfast

force-millilens: clean-millilens
	$(MAKE) millilens

force-millilens-lensed: clean-millilens-lensed
	$(MAKE) millilens-lensed

force-nonlensed-on-lensed: clean-nonlensed-on-lensed
	$(MAKE) nonlensed-on-lensed

force-summarise: clean-summarise
	$(MAKE) summarise

help:
	@echo "Targets:"
	@echo "  make / make bilby         Build bilby PE products (resume if interrupted)"
	@echo "  make cogwheel             Build cogwheel PE products (resume if interrupted)"
	@echo "  make gwfast               Build gwfast Fisher-matrix products"
	@echo "  make millilens            Millilensing PE on unlensed 01 data"
	@echo "  make millilens-lensed     Millilensing PE on a lensed two-image injection"
	@echo "  make nonlensed-on-lensed  Tutorial-01 PE (unlensed model) on lensed data"
	@echo "  make summarise            Evidences, Bayes factors, shared-parameter overlays"
	@echo "  make clean                Remove bilby output"
	@echo "  make clean-cogwheel       Remove cogwheel output"
	@echo "  make clean-gwfast         Remove gwfast output"
	@echo "  make clean-millilens      Remove millilensing-on-unlensed output"
	@echo "  make clean-millilens-lensed  Remove millilensing-on-lensed output"
	@echo "  make clean-nonlensed-on-lensed  Remove nonlensed-on-lensed output"
	@echo "  make clean-summarise      Remove summarise output"
	@echo "  make clean-all            Remove all tutorial outputs"
	@echo "  make force                Clean and rebuild bilby"
	@echo "  make force-cogwheel       Clean and rebuild cogwheel"
	@echo "  make force-gwfast         Clean and rebuild gwfast"
	@echo "  make force-millilens      Clean and rebuild millilens"
	@echo "  make force-millilens-lensed  Clean and rebuild millilens-lensed"
	@echo "  make force-nonlensed-on-lensed  Clean and rebuild nonlensed-on-lensed"
	@echo "  make force-summarise      Clean and rebuild summarise"
	@echo ""
	@echo "Bilby products:"
	@echo "  $(BILBY_WAVEFORMS)"
	@echo "  $(BILBY_CORNER)"
	@echo "  $(BILBY_RESULT)"
	@echo ""
	@echo "Cogwheel products:"
	@echo "  $(COGWHEEL_WAVEFORMS)"
	@echo "  $(COGWHEEL_CORNER)"
	@echo "  $(COGWHEEL_RESULT)"
	@echo ""
	@echo "gwfast products:"
	@echo "  $(GWFAST_WAVEFORMS)"
	@echo "  $(GWFAST_CORNER)"
	@echo "  $(GWFAST_RESULT)"
	@echo ""
	@echo "Millilens-on-unlensed products:"
	@echo "  $(MILLENS_WAVEFORMS)"
	@echo "  $(MILLENS_CORNER)"
	@echo "  $(MILLENS_CORNER_LENS)"
	@echo "  $(MILLENS_N1_PHASE)"
	@echo "  $(MILLENS_RESULT)"
	@echo ""
	@echo "Millilens-on-lensed products:"
	@echo "  $(MILLENS_LENSED_WAVEFORMS)"
	@echo "  $(MILLENS_LENSED_CORNER)"
	@echo "  $(MILLENS_LENSED_CORNER_LENS)"
	@echo "  $(MILLENS_LENSED_RESULT)"
	@echo ""
	@echo "Nonlensed-on-lensed products:"
	@echo "  $(NONLENSED_LENSED_WAVEFORMS)"
	@echo "  $(NONLENSED_LENSED_CORNER)"
	@echo "  $(NONLENSED_LENSED_RESULT)"
	@echo ""
	@echo "Summarise products:"
	@echo "  $(SUMMARISE_UNLENSED)"
	@echo "  $(SUMMARISE_LENSED)"
