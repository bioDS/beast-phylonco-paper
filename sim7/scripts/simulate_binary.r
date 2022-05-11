library('ape')
library('TreeSimGM')

# Simulates sequences with Binary substitution model down a tree
source("simulate_seq_binary.r")

get_error <- function(alpha, beta) {
	error <- matrix(c(
		1 - alpha, beta,
		alpha, 1 - beta), byrow=T, ncol=2)
	error
}

add_error <- function(x, alpha, beta) {
	seq <- rep(0, length(x))
	error_model <- get_error(alpha, beta)
	for (i in 1:length(x)) {
		state <- x[i]
		prob <- error_model[, state]
		seq[i] <- sample_from(prob)
	}
	seq
}

simulate_tree <- function(tree, n, l, lambda, alpha, beta) {
	Q <- get_q(lambda)
	freq <- get_pi(lambda)
	edges <- tree$edge
	lengths <- tree$edge.length
	labels <- as.numeric(tree$tip.label)
	N <- 2 * n - 1
	nodes <- vector(mode = "list", length = N)
	root <- generate_seq(l, freq)
	nodes[[n + 1]] <- root
	for (i in 1:dim(edges)[1]) {
		t <- lengths[i]
		parent_index <- edges[i, 1]
		child_index <- edges[i, 2]
		parent <- nodes[[parent_index]]
		child <- mutate_seq(parent, get_p(Q, t))
		nodes[[child_index]] <- child
	}
	# add error and translate seq
	tr_nodes <- vector(mode = "list", length = n)
	for (i in 1:n) {
		seq_errors <- add_error(nodes[[i]], alpha, beta)
		child_label <- labels[i]
		tr_nodes[[child_label]] <- translate_seq(seq_errors)
	}
	tr_nodes
}

simulate_trees_yule <- function(filename, n, l, num_trials, lambdas, alphas, betas, birthrates) {
  sink(file.path(output_dir, filename))
  cat("tree,lambda,alpha,beta,birthrate,treelength,treeheight,node,sequence\n")
  trees <- vector(mode = "list", length = num_trials)
  for (i in 1:num_trials) {
    lambda <- lambdas[i]
    alpha <- alphas[i]
    beta <- betas[i]
    birthrate <- birthrates[i]
    tree <- generate_tree(n = n, birthrate = birthrate)
    tree_length <- sum(tree$edge.length)
    tree_height <- max(node.depth.edgelength(tree))
    trees[i] <- write.tree(tree)
    seqs <- simulate_tree(tree, n, l, lambda, alpha, beta)
    for (j in 1:n) {
      cat(i, lambda, alpha, beta, birthrate, tree_length, tree_height, j, "", sep = ",")
      cat(seqs[[j]], "\n", sep = "")
    }
  }
  sink()
  # writing tree log
  tree_file <- paste0(gsub(pattern = '\\.[^\\.]*$', '', filename), '.trees')
  sink(file.path(output_dir, tree_file))
  cat(paste(unlist(trees)), sep='\n')
  sink()
}

# format tips
format_tree <- function(tree) {
	tree$root.edge <- 0.0
	tree$root <- 0.0
	labels <- tree$tip.label
	for (i in 1:length(labels)) {
		labels[i] <- gsub("[^<0-9>]*", "", labels[i])
	}
	tree$tip.label <- labels
	return(tree)
}

# generate Yule tree with n leaves
generate_tree <- function(n, birthrate = 1.5) {
    birth_param <- sprintf("rexp(%s)", birthrate)
    trees <- sim.taxa(numbsim = 1, n = n, waitsp = birth_param)
    tree <- trees[[1]]
	tree <- format_tree(tree)
	return(tree)
}

sequence_tag <- function(id, seq_data) {
    res <- paste0("<sequence taxon='", id, "'>\n")
    res <- paste0(res, "\t", seq_data, "\n")
    res <- paste0(res, "\t</sequence>\n")
    res
}

taxon_tag <- function(id) {
    res <- paste0("<taxon spec='Taxon' id='", id, "'/>\n")
    res
}

# create single beast xml
create_xml <- function(data, i, template, log_name, n, lambda_mu, birthrate_mu) {
    seqs_xml <- ""
    taxons_xml <- ""
    for (j in (1:n)) {
        seq <- data$sequence[data$tree == i & data$node == toString(j)]
        seqs_xml <- paste0(seqs_xml, sequence_tag(j, seq))
        taxons_xml <- paste0(taxons_xml, taxon_tag(j))
    }
    s <- gsub(pattern = "%seq_data%", replace = seqs_xml, x = template)
    s <- gsub(pattern = "%taxon_data%", replace = taxons_xml, x = s)
	s <- gsub(pattern = "%lambda_mu%", replace = lambda_mu, x = s)
	s <- gsub(pattern = "%logname%", replace = log_name, x = s)

	if (birthrate_mu > 0) {
	  s <- gsub(pattern = "%birthrate_mu%", replace = birthrate_mu, x = s)
	}

	return(s)
}

# create beast xmls
create_xmls <- function(seq_file, template_file, output_file, n, lambda_mu, birthrate_mu) {
	template_path <- file.path(template_file)
	seq_path <- file.path(output_dir, seq_file)
	template <- readLines(template_path)
	data <- read.csv(seq_path, colClasses = c("sequence" = "character"))
	N <- length(unique(data$tree))
	for (i in 1:N) {
		filename <- file.path(output_dir, sub("%num%", i, output_file))
		log_name <- sub(".xml", "", basename(filename))
		content <- create_xml(data, i, template, log_name, n, lambda_mu, birthrate_mu = birthrate_mu)
		writeLines(content, filename)
	}
}

run_simulation_yule <- function(alpha, beta, output_name) {
  seed <- 666
  n <- 16
  l <- 1000
  num_trials <- 20

  lambda_mu <- -1
  birthrate_mu <- 7

  lambdas <- rlnorm(num_trials, lambda_mu)
  alphas <- rep(alpha, num_trials)
  betas <- rep(beta, num_trials)
  birthrates <- rnorm(num_trials, birthrate_mu)

  seq_file <- paste0(output_name, "_true.csv")
  template_file <- "binary_template.xml"
  xml_file <- paste0(output_name, "_%num%.xml.temp")

  simulate_trees_yule(seq_file, n, l, num_trials, lambdas, alphas, betas, birthrates)
  create_xmls(seq_file, template_file, xml_file, n, lambda_mu, birthrate_mu = birthrate_mu)
}

# varying betas
output_dir <- "../data/binary_beta"
alpha <- 0.001
beta_list <- c(0.0, 0.1, 0.25, 0.5, 0.6)
for (beta in beta_list) {
    suffix <- toString(beta * 100)
    output_name <- paste0("binary_beta_", suffix)
    run_simulation_yule(alpha, beta, output_name)
}

# varying alphas
output_dir <- "../data/binary_alpha"
beta <- 0.5
alpha_list <- c(0.0, 0.001, 0.01, 0.05, 0.1)
for (alpha in alpha_list) {
    suffix <- toString(alpha * 100)
    output_name <- paste0("binary_alpha_", suffix)
    run_simulation_yule(alpha, beta, output_name)
}

