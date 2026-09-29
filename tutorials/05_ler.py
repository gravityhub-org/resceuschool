# Import LeR
from ler.rates.ler import LeR

# Initialize LeR with default settings
ler = LeR(npool=6) # You can change the waveforms, detectors, BBH population models, Lens population models, lens models, here.

# Sample non-lensed parameters:
unlensed_param = ler.unlensed_cbc_statistics(size=1000000, batch_size=50000, resume=True)
rate_unlensed, unlensed_param_detectable = ler.unlensed_rate()

# Sample lensed parameters:
lensed_param = ler.lensed_cbc_statistics(size=1000000, batch_size=50000, resume=True)
# include other useful parameters in the output dictionary.
# It is omitted by default to save runtime and memory.
# For theta_E, n_images, mass_1, mass_2, luminosity_distance:
lensed_param = ler.recover_redundant_parameters(lensed_param)
# For effective_luminosity_distance, effective_geocent_time, effective_phase, effective_ra, effective_dec:
lensed_param = ler.produce_effective_params(lensed_param)

# Calculate the detection rate for lensed events
rate_lensed, lensed_param_detectable = ler.lensed_rate()
lensed_param_detectable = ler.recover_redundant_parameters(lensed_param_detectable) # Same as before
lensed_param_detectable = ler.produce_effective_params(lensed_param_detectable) # Same as before

print(f"\n=== Lensed Detection Rate Summary ===")
print(f"Detectable event rate: {rate_lensed:.2e} events per year")
print(f"Total event rate: {ler.normalization_pdf_z_lensed:.2e} events per year")
print(f"Percentage fraction of the detectable events: {rate_lensed/ler.normalization_pdf_z_lensed*100:.2e}%")


