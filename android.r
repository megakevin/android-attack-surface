##########################################
#### Input and Output Methods Proportion

slices <- c(1.0989010989, 1.6483516484, 7.1428571429, 1.0989010989, 1.6483516484, 10.989010989, 4.6703296703, 4.3956043956, 1.0989010989, 1.0989010989, 10.7142857143, 1.9230769231, 1.0989010989, 12.0879120879, 14.010989010989015)
lbls <- c("android.app.usage", "android.preference", "android.app", "android.hardware.usb", "android.graphics", "android.app.admin", "java.io", "android.bluetooth", "android.app.backup", "android.accounts", "android.database", "android.media", "android.database.sqlite", "android.content.res", "other")
pie(slices, labels = lbls, 
    main="Input Methods per package", 
    col=rainbow(length(lbls)), 
    radius = 1, 
    cex = 0.7);

slices <- c(1.9736842105263157, 11.842105263157894, 28.947368421052634, 1.3157894736842104, 1.644736842105263, 9.210526315789473, 2.631578947368421, 1.9736842105263157, 3.289473684210526, 18.092105263157894, 5.263157894736842, 2.9605263157894735, 10.855263157894735)
lbls <- c("android.app.backup", "android.content", "android.widget", "android.accounts", "android.support.v7.media", "android.app", "android.database.sqlite", "android.os", "android.provider", "android.app.admin", "java.io", "android.bluetooth", "other")
pie(slices, labels = lbls, 
    main="Output Methods per package", 
    col=rainbow(length(lbls)), 
    radius = 1, 
    cex = 0.7);

###########################################
#### DATA
###########################################

data <- read.csv("/home/kevin/Desktop/android_data_final.csv", header = TRUE);
high <- subset(data, userrating >= 4.0);
low <- subset(data, userrating < 4.0);

max_num <- max(data$reviews_with_security_words);

data_subset = subset(data, reviews_with_security_words <= 50 & reviews_with_security_words > 0);

hist(data$reviews_with_security_words, 
     plot = 1, 
     breaks = 635, 
     main = "Histogram of Perceived Security Metric",
     xlab = "Reviews with security complaints"
);

hist(data_subset$reviews_with_security_words, 
     plot = 1, 
     breaks = 50, 
     main = "Histogram of Perceived Security Metric",
     xlab = "Reviews with security complaints");

## entry_points_count

cor(data$reviews_with_security_words, data$entry_points_count); # 0.07719178
cor.test(data$reviews_with_security_words, data$entry_points_count); # P < 0.05!
# t = 5.098, df = 3271, p-value = 3.627e-07

summary(data$entry_points_count)

hist(data$entry_points_count, 
     plot = 1, 
     breaks = max(data$entry_points_count), 
     main = "Histogram of number of entry points",
     xlab = "Number of entry points"
);

plot(data$reviews_with_security_words, 
     data$entry_points_count, 
     main="Entry Points and Security Complaints", 
     xlab="Reviews with security complaints", 
     ylab="Entry points count ", 
     pch=4)

wilcox.test(high$entry_points_count, 
            low$entry_points_count, 
            paired=FALSE); # P < 0.05!

wilcox.test(high$entry_points_count, 
            low$entry_points_count, 
            paired=FALSE,
            # alternative="greater",
            conf.int=TRUE);
#difference in location 
#5.999984 
#W = 1407300, p-value = 0.01163

boxplot((high$entry_points_count), 
        (low$entry_points_count), 
        main="Difference in the Entry Points",
        ylab="Entry Points",
        names=c("High Rated", "Low Rated"));

cor(data$userrating, data$entry_points_count); #
cor.test(data$userrating, data$entry_points_count); #

#entry_point_user_rating
plot(data$userrating, 
     data$entry_points_count, 
     main="Entry Points and User Rating", 
     xlab="User Rating", 
     ylab="Entry points count ", 
     pch=4)

## exit_points_count

cor(data$reviews_with_security_words, data$exit_points_count); # 0.06544354
cor.test(data$reviews_with_security_words, data$exit_points_count); # P < 0.05!
# t = 3.6184, df = 3271, p-value = 0.000301

summary(data$exit_points_count);

hist(data$exit_points_count, 
     plot = 1, 
     breaks = max(data$exit_points_count), 
     main = "Histogram of number of exit points",
     xlab = "Number of exit points"
);

plot(data$reviews_with_security_words, 
     data$exit_points_count, 
     main="Exit Points and Security Complaints", 
     xlab="Reviews with security complaints ", 
     ylab="Exit points count ", 
     pch=4)

wilcox.test(high$exit_points_count, 
            low$exit_points_count, 
            paired=FALSE,
            conf.int=TRUE); # P < 0.05!
#difference in location 
# 4.999946 
#W = 1446200, p-value = 7.378e-05

boxplot((high$exit_points_count), 
        (low$exit_points_count), 
        main="Difference in the Exit Points",
        ylab="Exit Points",
        names=c("High Rated", "Low Rated"));

cor(data$userrating, data$exit_points_count); #
cor.test(data$userrating, data$exit_points_count); #

#exit_point_user_rating
plot(data$userrating, 
     data$exit_points_count, 
     main="Exit Points and User Rating", 
     xlab="User Rating", 
     ylab="Exit points count", 
     pch=4)


## attack_surface_nodes_count

cor(data$reviews_with_security_words, data$attack_surface_nodes_count);
cor.test(data$reviews_with_security_words, data$attack_surface_nodes_count); # P < 0.05!

wilcox.test(high$attack_surface_nodes_count, 
            low$attack_surface_nodes_count, 
            paired=FALSE);

## average_closeness

cor(data$reviews_with_security_words, data$average_closeness);
cor.test(data$reviews_with_security_words, data$average_closeness);

wilcox.test(high$average_closeness, 
            low$average_closeness, 
            paired=FALSE); # P < 0.05!

## average_betweenness

cor(data$reviews_with_security_words, data$average_betweenness);
cor.test(data$reviews_with_security_words, data$average_betweenness);

wilcox.test(high$average_betweenness, 
            low$average_betweenness, 
            paired=FALSE);

## entry_points_clustering

cor(data$reviews_with_security_words, as.numeric(data$entry_points_clustering));
cor.test(data$reviews_with_security_words, as.numeric(data$entry_points_clustering)); # P < 0.05!

wilcox.test(as.numeric(high$entry_points_clustering), 
            as.numeric(low$entry_points_clustering), 
            paired=FALSE); # P < 0.05!

## exit_points_clustering

cor(data$reviews_with_security_words, as.numeric(data$exit_points_clustering));
cor.test(data$reviews_with_security_words, as.numeric(data$exit_points_clustering)); # P < 0.05!

wilcox.test(as.numeric(high$exit_points_clustering), 
            as.numeric(low$exit_points_clustering), 
            paired=FALSE);

## average_degree

cor(data$reviews_with_security_words, data$average_degree);
cor.test(data$reviews_with_security_words, data$average_degree); # P < 0.05!

wilcox.test(high$average_degree, 
            low$average_degree, 
            paired=FALSE); # P < 0.05!

## average_degree_centrality

cor(data$reviews_with_security_words, data$average_degree_centrality);
cor.test(data$reviews_with_security_words, data$average_degree_centrality);

wilcox.test(high$average_degree_centrality, 
            low$average_degree_centrality, 
            paired=FALSE); # P < 0.05!

## average_in_degree

cor(data$reviews_with_security_words, data$average_in_degree);
cor.test(data$reviews_with_security_words, data$average_in_degree); # P < 0.05!

wilcox.test(high$average_in_degree, 
            low$average_in_degree, 
            paired=FALSE); # P < 0.05!

## average_in_degree_centrality

cor(data$reviews_with_security_words, data$average_in_degree_centrality);
cor.test(data$reviews_with_security_words, data$average_in_degree_centrality);

wilcox.test(high$average_in_degree_centrality, 
            low$average_in_degree_centrality, 
            paired=FALSE); # P < 0.05!

## average_out_degree

cor(data$reviews_with_security_words, data$average_out_degree);
cor.test(data$reviews_with_security_words, data$average_out_degree); # P < 0.05!

wilcox.test(high$average_out_degree, 
            low$average_out_degree, 
            paired=FALSE); # P < 0.05!

## average_out_degree_centrality

cor(data$reviews_with_security_words, data$average_out_degree_centrality);
cor.test(data$reviews_with_security_words, data$average_out_degree_centrality);

wilcox.test(high$average_out_degree_centrality, 
            low$average_out_degree_centrality, 
            paired=FALSE); # P < 0.05!
