import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [userId, setUserId] = useState('');
  const [group, setGroup] = useState('');
  const [buttonColor, setButtonColor] = useState('#cccccc');
  const experimentId = 1;

  useEffect(() => {
    const newUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    setUserId(newUserId);

    axios.get(`http://localhost:8000/api/experiments/${experimentId}/assign-group/?user_id=${newUserId}`)
      .then(response => {
        const group = response.data.group;
        setGroup(group);
        setButtonColor(group === 'A' ? '#4A90E2' : '#50E3C2');
      })
      .catch(error => console.error('Ошибка получения группы:', error));
  }, []);

  const handleClick = () => {
    axios.post('http://localhost:8000/api/log-event/', {
      user_id: userId,
      experiment_id: experimentId,
      event_type: 'click',
      group: group,
    })
    .then(() => console.log('Событие отправлено'))
    .catch(error => console.error('Ошибка отправки:', error));
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh'
    }}>
      <button 
        onClick={handleClick}
        style={{
          backgroundColor: buttonColor,
          color: 'white',
          padding: '15px 30px',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontSize: '18px',
        }}
      >
        Нажми меня!
      </button>
    </div>
  );
};

export default App;