setwd("~/Desktop/cites data")
length(list.files(pattern=".csv"))
all <- list()
for(i in 1:length(list.files(pattern=".csv"))) {all[[i]] <- read.csv(list.files(pattern=".csv")[i],stringsAsFactors = F)}
base <- do.call("rbind",all)
base <- base[-unique(c(which(base$Importer %in% c("XX","XV","NT","ZZ","")),which(base$Exporter %in% c("XX","XV","NT","ZZ","")))),]
unique(c(base$Importer,base$Exporter))
write.csv(base,"wildthings.csv")
