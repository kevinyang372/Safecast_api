# Upload verifier

Safecast upload verifier api hosts a facilitative algorithm that could automatically classify the data uploaded by user into normal and abnormal points.


It contains two major functionalities:
## User Credibility Score
User credibility score is a static dataset hosted within the api which contains the credibility score of every recorded user.


The credibility score algorithm starts from one verified user (identified manually) 
and utilizes the BFS (Breadth First Algorithm) to traverse through the dataset. 


Throughout the process, it compares each data point with other
measurements in the nearby area. If the difference is within a certain range, it records the verification result of the data point as approved. 
Otherwise, it records the result as disproved.

### How to Use it
```POST / {"id": ["id1","id2"]}``` 

=> Gets the credibility score of id1 and id2

```GET / ```

=> Gets all credibility score of recorded users

## Single Measurement Verification
The API also allows requests with measurements data of one whole trip completed by a unique user. 
Upon receiving the request, for every single data in the trip, it establishes a set of measurements including the tested point and other historical data within a certain range.


Then by importing the set into an outlier detection algorithm, the api is able to classify each point as approved or disproved.

### How to Use it
``` POST /trip/ {[{"User": , "Drive": , "Latitude": , "Longitude": ", "Value": }...]}```

=> Post the measurements data to api for calculation

``` GET /trip/ {"user": } / {"drive": } / {"user": ,"drive": }```

=> Get the calculation results filtered by user and drive id.
