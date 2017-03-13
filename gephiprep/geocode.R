setwd("~/Desktop")
cc <- gdata::read.xls("ISOCountryCodes081507.xls")
cc[,c("lon","lat")] <- NA
cc$Country <- as.character(cc$Country)
require(ggmap)
for(i in 1:nrow(cc)){cc[i,3:4] <- geocode(cc$Country[i])}
cc[50,3:4] <- geocode("Czechoslovakia")
ac <- unique(c(base$Importer,base$Exporter))
ac[is.na(ac)] <- "NA"
cc <- cc[which(toupper(cc$Code) %in% ac),]
cc[cc$Country=="Georgia",3:4] <- geocode("Country Georgia")
cc[cc$Country=="Saint Helena",3:4] <- geocode("Country Saint Helena")
write.csv(cc,"country_loc.csv")

library(rworldmap)
newmap <- getMap(resolution = "low")
plot(newmap, asp = 1)
points(cc$lon,cc$lat,cex=0.2,col="red",pch=19)

