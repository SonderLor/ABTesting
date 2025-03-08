import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

const App = () => {
  const [userId, setUserId] = useState('');
  const [group, setGroup] = useState('');
  const [buttonColor, setButtonColor] = useState('#cccccc');
  const experimentId = 1;

  useEffect(() => {
    const newUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    setUserId(newUserId);

    axios.get(`http://localhost/api/experiments/${experimentId}/assign-group/?user_id=${newUserId}`, {
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      }
    })
      .then(response => {
        const group = response.data.group;
        setGroup(group);
        setButtonColor(group === 'A' ? '#4A90E2' : '#50E3C2');
      })
      .catch(error => console.error('Ошибка получения группы:', error));
      
    axios.post('http://localhost/api/events/', {
      user_id: newUserId,
      experiment: experimentId,
      event_type: 'view',
    }, {
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      }
    })
    .then(() => console.log('Событие отправлено в Postgres'))
    .catch(error => console.error('Ошибка отправки в Postgres:', error));
  }, []);

  const handleClick = () => {
    axios.post('http://localhost/api/log-event/', {
      user_id: userId,
      experiment: experimentId,
      event_type: 'click',
      group: group,
    }, {
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      }
    })
    .then(() => console.log('Событие отправлено в Mongo'))
    .catch(error => console.error('Ошибка отправки в Mongo:', error));

    axios.post('http://localhost/api/events/', {
      user_id: userId,
      experiment: experimentId,
      event_type: 'click',
    }, {
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken')
      }
    })
    .then(() => console.log('Событие отправлено в Postgres'))
    .catch(error => console.error('Ошибка отправки в Postgres:', error));
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
