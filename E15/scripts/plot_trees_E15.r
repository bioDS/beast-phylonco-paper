library("tools")
library("ggtree")
library("treeio")
library("ggplot2")

# E15 trees no outgroup
tree_error <- "../beast/E15_rskycoal_em_fast_summary.trees"

tree_no_error <- "../beast/E15_rskycoal_fast_summary.trees"

labels_file <- "../data/E15_labels.csv"

xlim <- -1
p <- 0.3
my_colors <-  c("#00BFC4", "#7CAE00", "#CEE39A")

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
    axis.text.x=element_text(size=11), #, hjust=-0.01),
    axis.title.x=element_text(size=11, hjust=0.95), 
    plot.caption=element_text(size=11),
    legend.title=element_text(size=11), 
    legend.text=element_text(size=11)) +
labs(color = "Cell type") 

revts(g1) +
xlim_tree(xlim) +
xlab("mutations per site") + 
scale_x_continuous(labels=abs) 

output_path <- '../figures/E15_gt16_error_tree.pdf'
ggsave(output_path, width = 6, height = 4, units = c("in"))
print(paste("figure saved:", file_path_as_absolute(output_path)))


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
    axis.text.x=element_text(size=11), #, hjust=-0.01),
    axis.title.x=element_text(size=11, hjust=0.95), 
    plot.caption=element_text(size=11),
    legend.title=element_text(size=11), 
    legend.text=element_text(size=11)) +
labs(color = "Cell type") 

revts(g2) +
xlim_tree(xlim) +
xlab("mutations per site") + 
scale_x_continuous(labels=abs) 

output_path <- '../figures/E15_gt16_no_error_tree.pdf'
ggsave(output_path, width = 6, height = 4, units = c("in"))
print(paste("figure saved:", file_path_as_absolute(output_path)))

