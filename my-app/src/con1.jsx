
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { debounce } from 'lodash';
import InfiniteScroll from 'react-infinite-scroll-component';
import './con1style.css';

const ContentDisplay = () => {
    const [newsData, setNewsData] = useState([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loading, setLoading] = useState(false);

    const fetchMoreData = async () => {
        if (loading) return;
        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:5000/generate_content?page=${page}&page_size=10`);
            setNewsData(prevData => [...prevData, ...response.data]);
            if (response.data.length === 0) {
                setHasMore(false);
            } else {
                setPage(prevPage => prevPage + 1);
            }
        } catch (error) {
            console.error('Error fetching news:', error);
            setHasMore(false);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchMoreData();
    }, []);

    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };

    return (
        <div className="App">
            
            <InfiniteScroll
                dataLength={newsData.length}
                next={fetchMoreData}
                hasMore={hasMore}
                loader={<h4>Loading...</h4>}
                endMessage={<p>No more data to load</p>}
            >
                {newsData.map((content, index) => (
                    <div key={index} className="content-card">
                        <h2 className="content-title">{content.title}</h2>
                        <p className="content-description">{content.description}</p>
                        {content.image && <img className="content-image" src={content.image} alt={content.title} />}
                        <p className="content-summary">{content.summary}</p>
                        <p className="content-keywords">Keywords: {content.keywords.join(', ')}</p>
                        <p className="content-url">
                            URL: <a href={content.url} target="_blank" rel="noopener noreferrer">{content.url}</a>
                        </p>
                    </div>
                ))}
            </InfiniteScroll>
            {newsData.length > 0 && (
                <button className="scroll-to-top-btn" onClick={scrollToTop}>
                    Scroll to Top
                </button>
            )}
        </div>
    );
};

export default ContentDisplay;