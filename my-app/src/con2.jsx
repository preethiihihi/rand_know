import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { debounce } from 'lodash';

const News = () => {
    const [newsData, setNewsData] = useState(null); // Initialize as null to check if data is fetched
    const [loading, setLoading] = useState(true); // Track loading state
    const fetchData = debounce(async () => {
     try {
         const response = await axios.get('http://localhost:5000/fetch_news');
         setNewsData(response.data);
         setLoading(false)
         //console.log('Data fetched:', response.data);
     } catch (error) {
         console.error('Error fetching data:', error);
     }
 }, 1000); // Debounce for 1 second (1000 milliseconds)
 
 useEffect(() => {
     fetchData();
 }, []);

    if (loading) {
        return <div>Loading...</div>; // Show loading indicator while fetching data
    }

    if (!newsData) {
        return <div>No news data available</div>; // Show message if no data is available
    }

    return (
     <div className="news">
     <h1>Latest News</h1>
     {newsData.map((news, index) => (
         <div key={index} className="news-card">
             <h2>{news.story_title}</h2>
             <p>{news.story_description}</p>
             <p className="metadata">Section: {news.section}</p>
             <p className="metadata">Published: {news.story_time}</p>
             <a href={news.web_url} target="_blank" rel="noopener noreferrer">Read More</a>
             <hr />
         </div>
     ))}
 </div>
    );
};

export default News;
