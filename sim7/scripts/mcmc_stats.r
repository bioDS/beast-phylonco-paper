library("tools")
library("TraceR")

mcmc_path <- "../beast"

burnin <- 0.1
files <- dir(path=mcmc_path, pattern=".log")

for (f in files) {
	mcmc_log <- readMCMCLog(file.path(mcmc_path, f))
	traces <- getTraces(mcmc_log, burn.in=burnin)
	stats <- analyseTraces(traces)
	out <- paste0(file_path_sans_ext(basename(f)), "_stats.log")
	write_tsv(stats, out)
}
