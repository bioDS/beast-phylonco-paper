library('expm')

# Implements a general Binary substitution model 

# states
states <- c("0", "1")

# get the equilibrium state frequencies
get_pi <- function(lambda) {
  pi0 <- lambda / (lambda + 1)
  pi1 <- 1 / (lambda + 1)
  c(pi0, pi1)
}

# get the normalization factor for the Q matrix
get_beta <- function(lambda) {
  freq <- get_pi(lambda)
  diag <- c(1, lambda)
  as.vector(1 / (freq %*% diag))
}

# get the normalized Q transition matrix
get_q <- function(lambda) {
  Q <- matrix(c(-1, 1, 
    lambda, -lambda), byrow=T, ncol=2)
  beta <- get_beta(lambda)
  beta * Q
}

# get the P matrix P(t) = exp(Qt)
get_p <- function(Q, t) { 
  expm(Q * t)
}

# sample from a given probability vector
sample_from <- function(prob) {  
  cum_prob <- cumsum(prob)
  r <- runif(1)
  for (i in 1:length(cum_prob)) {
    if (r < cum_prob[i]) {
      return (i)
    }
  }
}

# generate sequence from frequencies
generate_seq <- function(l, freq) {
  seq <- rep(0, l)
  for (i in 1:l) {
    seq[i] <- sample_from(freq)
  }
  seq
}

# mutate sequence
mutate_seq <- function(seq, P) {
  child_seq <- seq
  for (i in 1:length(seq)) {
    prob <- P[child_seq[i], ]
    child_seq[i] <- sample_from(prob)
  }
  child_seq
}

# translate from state index to actual states
translate_seq <- function(seq) {
  state_seq <- rep(states[1], length(seq))  
  for (i in 1:length(seq)) {
    state_seq[i] = states[seq[i]]    
  }
  state_seq
}