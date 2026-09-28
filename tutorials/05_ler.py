# Import LeR
from ler.rates.ler import LeR

# Initialize LeR with default settings
ler = LeR(npool=6)
# ler = LeR(
#     # if you want SNR values in the output, besides the boolean detection probability values
#     pdet_kwargs=dict(
#         snr_th=10.0,
#         snr_th_net=10.0,
#         pdet_type="boolean",
#         distribution_type="noncentral_chi2", # or 'fixed_snr' if you want to use optimal_snr values, instead of observed_snr values, in pdet calculation.
#         include_optimal_snr=True,
#         include_observed_snr=True)
#     # if you want to use spin precessing waveforms
#     waveform_approximant = 'IMRPhenomXPHM',
#     snr_recalculation = True,
#     snr_recalculation_range = [6, 14],
#     snr_recalculation_waveform_approximant = 'IMRPhenomXPHM',
#     # ler settings to access spin precessing GW parameters
#     spin_zero = False,
#     spin_precession=True,
# )


# Sample non-lensed parameters:
unlensed_param = ler.unlensed_cbc_statistics(size=100000, batch_size=50000, resume=True)
rate_unlensed, unlensed_param_detectable = ler.unlensed_rate()

# Sample lensed parameters:
lensed_param = ler.lensed_cbc_statistics(size=100000, batch_size=50000, resume=True)




