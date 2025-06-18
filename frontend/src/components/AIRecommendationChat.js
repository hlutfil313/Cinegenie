import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Paper, List, ListItem, ListItemText, CircularProgress } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import axios from 'axios';

const AIRecommendationChat = () => {
    const [input, setInput] = useState('');
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [chatHistory, setChatHistory] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        // Add user message to chat history
        const userMessage = { type: 'user', content: input };
        setChatHistory(prev => [...prev, userMessage]);
        setLoading(true);

        try {
            const response = await axios.post('/api/recommendations/chat-recommendations', {
                user_input: input
            });

            // Add AI response to chat history
            const aiMessage = {
                type: 'ai',
                content: 'Here are some recommendations based on your request:',
                recommendations: response.data.recommendations
            };
            setChatHistory(prev => [...prev, aiMessage]);
            setRecommendations(response.data.recommendations);
        } catch (error) {
            console.error('Error getting recommendations:', error);
            // Add error message to chat history
            setChatHistory(prev => [...prev, {
                type: 'error',
                content: 'Sorry, I encountered an error while getting recommendations.'
            }]);
        } finally {
            setLoading(false);
            setInput('');
        }
    };

    return (
        <Box sx={{ maxWidth: 800, margin: '0 auto', p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Gemini AI Movie Recommendations
            </Typography>
            
            {/* Chat History */}
            <Paper 
                elevation={3} 
                sx={{ 
                    height: 400, 
                    mb: 2, 
                    p: 2, 
                    overflow: 'auto',
                    backgroundColor: '#f5f5f5'
                }}
            >
                {chatHistory.map((message, index) => (
                    <Box
                        key={index}
                        sx={{
                            display: 'flex',
                            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                            mb: 2
                        }}
                    >
                        <Paper
                            elevation={1}
                            sx={{
                                p: 2,
                                maxWidth: '70%',
                                backgroundColor: message.type === 'user' ? '#e3f2fd' : '#ffffff'
                            }}
                        >
                            <Typography variant="body1">
                                {message.content}
                            </Typography>
                            
                            {message.type === 'ai' && message.recommendations && (
                                <List>
                                    {message.recommendations.map((movie, idx) => (
                                        <ListItem key={idx}>
                                            <ListItemText
                                                primary={movie.title}
                                                secondary={`${movie.overview?.substring(0, 100)}...`}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            )}
                        </Paper>
                    </Box>
                ))}
                {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                        <CircularProgress />
                    </Box>
                )}
            </Paper>

            {/* Input Form */}
            <Paper 
                component="form" 
                onSubmit={handleSubmit}
                sx={{ 
                    p: 2,
                    display: 'flex',
                    gap: 1
                }}
            >
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Describe what kind of movie you're looking for..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                />
                <Button
                    type="submit"
                    variant="contained"
                    endIcon={<SendIcon />}
                    disabled={loading || !input.trim()}
                >
                    Send
                </Button>
            </Paper>

            {/* Example Prompts */}
            <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                    Try asking for recommendations like:
                </Typography>
                <List>
                    <ListItem>
                        <ListItemText 
                            primary="I want to watch something like Inception but less complicated"
                            secondary="Gemini AI will understand the reference and find similar movies"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText 
                            primary="Show me movies that would be good for a first date"
                            secondary="Gemini AI will consider the context and suggest appropriate movies"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText 
                            primary="I'm feeling nostalgic for 90s movies"
                            secondary="Gemini AI will understand the time period and mood"
                        />
                    </ListItem>
                </List>
            </Box>
        </Box>
    );
};

export default AIRecommendationChat; 