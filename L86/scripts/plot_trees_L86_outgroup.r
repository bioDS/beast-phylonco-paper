library(ggtree)
library(treeio)
library(ggplot2)

# L86 trees outgroup
tree_error <- "../beast/L86_rskycoal_em_outgroup_summary.trees"
tree_no_error <- "../beast/L86_rskycoal_outgroup_summary.trees"

labels_file <- "~../data/L86_labels.csv"

xlim <- -0.15
p <- 0.3
my_colors <-  c("#00BFC4", "#B8E4E5", "#7CAE00", "#CEE39A")

labels <- read.csv(labels_file)

# tree 1
beast_error <- read.beast(tree_error)
tree1 <- full_join(beast_error, labels, by='label')

# tree 2
beast_no_error <- read.beast(tree_no_error)
tree2 <- full_join(beast_no_error, labels, by='label')

# tree 1
g1 <- ggtree(tree1) + # geom_tiplab(size = 2) + 
geom_tippoint(shape=15, aes(color=group), size=1.5) + 
geom_range("height_0.95_HPD", color="grey", size=3, alpha=0.3) +
geom_text2(aes(label=100*round(as.numeric(posterior), 2), 
      subset=(!length==0 & as.numeric(posterior) > p), 
      x=branch), vjust=-0.2, size=2.5) +
scale_color_manual(values=my_colors) + 
theme_tree2() + 
theme(legend.position="bottom",
    axis.text.x=element_text(size=14), #, hjust=-0.01),
    axis.title.x=element_text(size=14, hjust=0.95), 
    plot.caption=element_text(size=14),
    legend.title=element_text(size=14), 
    legend.text=element_text(size=14)) +
labs(color = "Cell type") 

revts(g1) +
xlim_tree(xlim) +
xlab("mutations per site") + 
scale_x_continuous(labels=abs) 

ggsave('../figures/L86_gt16_outgroup_error_tree.pdf', width = 8, height = 7.5, units = c("in"))

# tree 2
g2 <- ggtree(tree2) + # geom_tiplab(size = 2) + 
geom_tippoint(shape=15, aes(color=group), size=1.5) + 
geom_range("height_0.95_HPD", color="grey", size=3, alpha=0.3) +
geom_text2(aes(label=100*round(as.numeric(posterior), 2), 
      subset=(!length==0 & as.numeric(posterior) > p), 
      x=branch), vjust=-0.2, size=2.5) +
scale_color_manual(values=my_colors) + 
theme_tree2() + 
theme(legend.position="bottom",
    axis.text.x=element_text(size=14), #, hjust=-0.01),
    axis.title.x=element_text(size=14, hjust=0.95), 
    plot.caption=element_text(size=14),
    legend.title=element_text(size=14), 
    legend.text=element_text(size=14)) +
labs(color = "Cell type") 

revts(g2) +
xlim_tree(xlim) +
xlab("mutations per site") + 
scale_x_continuous(labels=abs) 

ggsave('../figures/L86_gt16_outgroup_no_error_tree.pdf', width = 8, height = 7.5, units = c("in"))

