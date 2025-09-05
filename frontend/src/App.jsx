import { useState } from 'react';
import {
  Container,
  Title,
  Text,
  Stack,
  TextInput,
  Textarea,
  Button,
  Loader,
  Card,
  Group,
  Alert,
} from '@mantine/core';
import { motion, AnimatePresence } from 'framer-motion';
// We don't need to import App.css here as it's handled globally in main.jsx

function App() {
  const [formData, setFormData] = useState({
    academic_background: '',
    interests: '',
    strengths: '',
    personality_traits: '',
    preferred_industries: '',
  });

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRecommendations([]);

    const profile = {
      ...formData,
      interests: formData.interests.split(',').map(s => s.trim()),
      strengths: formData.strengths.split(',').map(s => s.trim()),
      personality_traits: formData.personality_traits.split(',').map(s => s.trim()),
      preferred_industries: formData.preferred_industries.split(',').map(s => s.trim()),
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setRecommendations(data);

    } catch (err) {
      setError('Failed to fetch recommendations. Is the backend server running?');
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size="sm" my="xl">
      <Stack align="center" ta="center" mb="xl">
        <Title order={1}>🚀 AI Career Guidance Path</Title>
        <Text c="dimmed">Your personal guide to discovering the perfect career.</Text>
      </Stack>

      <Card withBorder radius="md" p="xl">
        <form onSubmit={handleSubmit}>
          <Stack>
            <TextInput
              name="academic_background"
              label="Academic Background"
              placeholder="e.g., Bachelor's in Arts"
              value={formData.academic_background}
              onChange={handleChange}
              required
            />
            <Textarea
              name="interests"
              label="Interests & Hobbies (comma-separated)"
              placeholder="e.g., painting, problem solving"
              value={formData.interests}
              onChange={handleChange}
              required
            />
            <Textarea
              name="strengths"
              label="Strengths (comma-separated)"
              placeholder="e.g., creativity, communication"
              value={formData.strengths}
              onChange={handleChange}
              required
            />
            <Textarea
              name="personality_traits"
              label="Personality Traits (comma-separated)"
              placeholder="e.g., analytical, outgoing"
              value={formData.personality_traits}
              onChange={handleChange}
              required
            />
             <Textarea
              name="preferred_industries"
              label="Preferred Industries (comma-separated)"
              placeholder="e.g., tech, finance, design"
              value={formData.preferred_industries}
              onChange={handleChange}
              required
            />
            <Button type="submit" size="md" fullWidth loading={loading} mt="md">
              ✨ Generate My Career Path
            </Button>
          </Stack>
        </form>
      </Card>

      {error && (
        <Alert color="red" title="An Error Occurred" mt="lg">
          {error}
        </Alert>
      )}

      {recommendations.length > 0 && (
        <Stack mt="xl">
          <Title order={2} ta="center">Your Top Career Recommendations</Title>
          <AnimatePresence>
            {recommendations.map((rec, index) => (
              <motion.div
                key={rec.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card withBorder radius="md" p="lg" mt="sm">
                  <Title order={3} size="h4">{rec.title}</Title>
                  <Text c="dimmed" size="sm" mt={4}>{rec.description}</Text>
                  <Text size="xs" mt="sm" c="blue">Match Score: {rec.match_score}</Text>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </Stack>
      )}
    </Container>
  );
}

export default App;

