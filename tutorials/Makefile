# RESCEU GW lensing school tutorials
#
#   make / make all       # full pipeline: bilby + gwfast + millilens(+lensed) + nonlensed-on-lensed + summarise
#   make bilby            # tutorial-01 unlensed PE
#   make gwfast           # gwfast Fisher-matrix products
#   make millilens        # millilensing PE on unlensed 01 data
#   make millilens-lensed # millilensing PE on a lensed two-image injection
#   make nonlensed-on-lensed  # tutorial-01 PE (unlensed model) on that lensed signal
#   make summarise        # evidences, Bayes factors, overlays + lens recovery
#   make ler              # LeR rates (05) + forecast PDFs (06)
#   make forecasts        # LeR forecast PDFs from ler_data (06; needs ler)
#   make clean / clean-gwfast / clean-millilens / clean-millilens-lensed /
#        clean-nonlensed-on-lensed / clean-summarise / clean-ler /
#        clean-forecasts / clean-all
#   make force / force-gwfast / force-millilens / force-millilens-lensed /
#        force-nonlensed-on-lensed / force-summarise / force-ler /
#        force-forecasts / force-all
#
# Products are file targets, so a completed run is a no-op. Interrupted
# sampling runs resume from the sampler checkpoint (same cached injection).
# Editing the script does not rebuild by itself — use `make force*`.
#
# Parallelism: bilby dynesty uses NPOOL workers (default 8). Independent
# targets can also be built concurrently, e.g. `make -j3 bilby millilens-lensed gwfast`.
UV ?= uv
# Headless plotting (bilby / matplotlib); override with e.g. MPLBACKEND=TkAgg if needed.
export MPLBACKEND ?= Agg
# Dynesty worker processes per bilby run (override with NPOOL=...).
export NPOOL ?= 8

# --- bilby (tutorial 01) ---
BILBY_SCRIPT := 01_parameter_estimation.py
BILBY_OUTDIR := output/01_parameter_estimation
BILBY_RUNDIR := $(BILBY_OUTDIR)/bilby_run
BILBY_LABEL := lhvk_distance_demo
BILBY_WAVEFORMS := $(BILBY_OUTDIR)/lhvk_waveforms.png
BILBY_CORNER := $(BILBY_OUTDIR)/posterior_corner.png
BILBY_RESULT := $(BILBY_RUNDIR)/$(BILBY_LABEL)_result.json
BILBY_PRODUCTS := $(BILBY_WAVEFORMS) $(BILBY_CORNER) $(BILBY_RESULT)
# Shared strain cache produced by tutorial 01 (also used by millilens).
BILBY_IFO_CACHE := $(BILBY_RUNDIR)/injection_ifos.npz

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
SUMMARISE_LENS_RECOVERY_UNLENSED := $(SUMMARISE_OUTDIR)/lens_recovery_unlensed_injection.png
SUMMARISE_LENS_RECOVERY_LENSED := $(SUMMARISE_OUTDIR)/lens_recovery_lensed_injection.png
SUMMARISE_PRODUCTS := $(SUMMARISE_UNLENSED) $(SUMMARISE_LENSED) \
	$(SUMMARISE_LENS_RECOVERY_UNLENSED) $(SUMMARISE_LENS_RECOVERY_LENSED)

# --- LeR rates (tutorial 05) ---
LER_SCRIPT := 05_ler.py
LER_DATADIR := ler_data
LER_UNLENSED := $(LER_DATADIR)/unlensed_param.json
LER_UNLENSED_DET := $(LER_DATADIR)/unlensed_param_detectable.json
LER_LENSED := $(LER_DATADIR)/lensed_param.json
LER_LENSED_DET := $(LER_DATADIR)/lensed_param_detectable.json
LER_PRODUCTS := $(LER_UNLENSED) $(LER_UNLENSED_DET) $(LER_LENSED) $(LER_LENSED_DET)

# --- LeR forecast plots (tutorial 06) ---
FORECAST_SCRIPT := 06_plot_forecasts.py
FORECAST_OUTDIR := forecasts
FORECAST_PRODUCTS := \
	$(FORECAST_OUTDIR)/sl_intrinsic_source_redshift.pdf \
	$(FORECAST_OUTDIR)/detectable_source_redshift.pdf \
	$(FORECAST_OUTDIR)/comparison_source_redshift.pdf \
	$(FORECAST_OUTDIR)/sl_intrinsic_velocity_dispersion_vs_redshift.pdf \
	$(FORECAST_OUTDIR)/detectable_velocity_dispersion_vs_redshift.pdf \
	$(FORECAST_OUTDIR)/comparison_velocity_dispersion_vs_redshift.pdf \
	$(FORECAST_OUTDIR)/sl_intrinsic_einstein_radius.pdf \
	$(FORECAST_OUTDIR)/detectable_einstein_radius.pdf \
	$(FORECAST_OUTDIR)/comparison_einstein_radius.pdf \
	$(FORECAST_OUTDIR)/sl_intrinsic_time_delays.pdf \
	$(FORECAST_OUTDIR)/detectable_time_delays.pdf \
	$(FORECAST_OUTDIR)/comparison_time_delays.pdf

.PHONY: all bilby gwfast millilens millilens-lensed nonlensed-on-lensed summarise \
	ler forecasts \
	clean clean-gwfast clean-millilens clean-millilens-lensed \
	clean-nonlensed-on-lensed clean-summarise clean-ler clean-forecasts clean-all \
	force force-gwfast force-millilens force-millilens-lensed \
	force-nonlensed-on-lensed force-summarise force-ler force-forecasts force-all help

# Full tutorial pipeline. `summarise` pulls in 01/02/03m/03n via result deps;
# gwfast is independent. LeR/forecasts are separate (heavy sampling). Use
# `make -j` to overlap independent PE runs.
all: summarise gwfast

bilby: $(BILBY_PRODUCTS)

gwfast: $(GWFAST_PRODUCTS)

millilens: $(MILLENS_PRODUCTS)

millilens-lensed: $(MILLENS_LENSED_PRODUCTS)

nonlensed-on-lensed: $(NONLENSED_LENSED_PRODUCTS)

summarise: $(SUMMARISE_PRODUCTS)

# Rates JSON from 05, then forecast PDFs from 06 (06 already depends on LER_PRODUCTS).
ler: $(LER_PRODUCTS) $(FORECAST_PRODUCTS)

forecasts: $(FORECAST_PRODUCTS)

# Grouped targets (GNU make ≥ 4.3): one recipe, no re-run once products exist.
$(BILBY_PRODUCTS) &:
	$(UV) run python $(BILBY_SCRIPT)
	@test -f $(BILBY_WAVEFORMS)
	@test -f $(BILBY_CORNER)
	@test -f $(BILBY_RESULT)

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

# Prefer the shared lensed strain cache from millilens-lensed when present;
# the script can also create that cache itself if missing.
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
	@test -f $(SUMMARISE_LENS_RECOVERY_UNLENSED)
	@test -f $(SUMMARISE_LENS_RECOVERY_LENSED)

# LeR writes under ler_data/; resume=True makes re-runs cheap once JSONs exist.
$(LER_PRODUCTS) &:
	$(UV) run python $(LER_SCRIPT)
	@test -f $(LER_UNLENSED)
	@test -f $(LER_UNLENSED_DET)
	@test -f $(LER_LENSED)
	@test -f $(LER_LENSED_DET)

# Forecast PDFs need the LeR JSONs; 06 regenerates detectable lensed if missing.
$(FORECAST_PRODUCTS) &: $(LER_PRODUCTS)
	$(UV) run python $(FORECAST_SCRIPT)
	@test -f $(FORECAST_OUTDIR)/sl_intrinsic_source_redshift.pdf
	@test -f $(FORECAST_OUTDIR)/detectable_source_redshift.pdf
	@test -f $(FORECAST_OUTDIR)/comparison_source_redshift.pdf
	@test -f $(FORECAST_OUTDIR)/sl_intrinsic_velocity_dispersion_vs_redshift.pdf
	@test -f $(FORECAST_OUTDIR)/detectable_velocity_dispersion_vs_redshift.pdf
	@test -f $(FORECAST_OUTDIR)/comparison_velocity_dispersion_vs_redshift.pdf
	@test -f $(FORECAST_OUTDIR)/sl_intrinsic_einstein_radius.pdf
	@test -f $(FORECAST_OUTDIR)/detectable_einstein_radius.pdf
	@test -f $(FORECAST_OUTDIR)/comparison_einstein_radius.pdf
	@test -f $(FORECAST_OUTDIR)/sl_intrinsic_time_delays.pdf
	@test -f $(FORECAST_OUTDIR)/detectable_time_delays.pdf
	@test -f $(FORECAST_OUTDIR)/comparison_time_delays.pdf

clean:
	rm -rf $(BILBY_OUTDIR)

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

clean-ler:
	rm -rf $(LER_DATADIR)

clean-forecasts:
	rm -rf $(FORECAST_OUTDIR)

clean-all: clean clean-gwfast clean-millilens clean-millilens-lensed \
	clean-nonlensed-on-lensed clean-summarise clean-ler clean-forecasts

force: clean
	$(MAKE) bilby

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

force-ler: clean-ler clean-forecasts
	$(MAKE) ler

force-forecasts: clean-forecasts
	$(MAKE) forecasts

force-all: clean-all
	$(MAKE) all
	$(MAKE) ler

help:
	@echo "Targets:"
	@echo "  make / make all           Full pipeline (PE runs + summarise + gwfast)"
	@echo "  make bilby                Tutorial-01 unlensed PE (resume if interrupted)"
	@echo "  make gwfast               gwfast Fisher-matrix products"
	@echo "  make millilens            Millilensing PE on unlensed 01 data"
	@echo "  make millilens-lensed     Millilensing PE on a lensed two-image injection"
	@echo "  make nonlensed-on-lensed  Tutorial-01 PE (unlensed model) on lensed data"
	@echo "  make summarise            Evidences, Bayes factors, overlays + lens recovery"
	@echo "  make ler                  LeR rates (05) + forecast PDFs (06)"
	@echo "  make forecasts            LeR forecast PDFs only (06; builds rates if needed)"
	@echo "  make clean                Remove bilby (01) output"
	@echo "  make clean-gwfast         Remove gwfast output"
	@echo "  make clean-millilens      Remove millilensing-on-unlensed output"
	@echo "  make clean-millilens-lensed  Remove millilensing-on-lensed output"
	@echo "  make clean-nonlensed-on-lensed  Remove nonlensed-on-lensed output"
	@echo "  make clean-summarise      Remove summarise output"
	@echo "  make clean-ler            Remove ler_data/"
	@echo "  make clean-forecasts      Remove forecasts/"
	@echo "  make clean-all            Remove all tutorial outputs (incl. ler/forecasts)"
	@echo "  make force / force-*      Clean and rebuild a target (force-all = PE + ler plots)"
	@echo ""
	@echo "Environment (exported to recipes):"
	@echo "  MPLBACKEND=$(MPLBACKEND)   matplotlib backend (default Agg for headless)"
	@echo "  NPOOL=$(NPOOL)             dynesty worker processes per bilby run"
	@echo ""
	@echo "Bilby (01) products:"
	@echo "  $(BILBY_WAVEFORMS)"
	@echo "  $(BILBY_CORNER)"
	@echo "  $(BILBY_RESULT)"
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
	@echo ""
	@echo "LeR (05) products:"
	@echo "  $(LER_UNLENSED)"
	@echo "  $(LER_UNLENSED_DET)"
	@echo "  $(LER_LENSED)"
	@echo "  $(LER_LENSED_DET)"
	@echo ""
	@echo "Forecast (06) products: $(FORECAST_OUTDIR)/{sl_intrinsic,detectable,comparison}_*.pdf"
