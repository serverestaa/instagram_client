import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import './Profile.css';
import DefaultProfilePic from './default.png';

const BASE_URL = 'http://localhost:8000/';

function Profile({ authToken, authTokenType, userId: loggedInUserId }) {
  const { userId: paramUserId } = useParams();
  const [userProfile, setUserProfile] = useState(null);
  const [userPosts, setUserPosts] = useState([]);

  // Determine the correct userId to fetch: use `paramUserId` if viewing another user's profile, otherwise `loggedInUserId`.
  const userIdToFetch = paramUserId || loggedInUserId;

  // Fetch user profile information
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch(`${BASE_URL}user/profile/${userIdToFetch}`, {
          headers: authToken ? { 'Authorization': `${authTokenType} ${authToken}` } : {},
        });
        if (!response.ok) throw new Error('Failed to fetch user profile');
        const profileData = await response.json();
        setUserProfile(profileData);
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
      }
    };

    if (userIdToFetch) {
      fetchProfile();
    }
  }, [authToken, authTokenType, userIdToFetch]);

  // Fetch user-specific posts
  useEffect(() => {
    const fetchUserPosts = async () => {
      try {
        const response = await fetch(`${BASE_URL}post/user/${userIdToFetch}`, {
          headers: authToken ? { 'Authorization': `${authTokenType} ${authToken}` } : {},
        });
        if (!response.ok) throw new Error('Failed to fetch user posts');
        const postsData = await response.json();
        setUserPosts(postsData);
      } catch (error) {
        console.error("Error fetching user posts:", error);
        alert('Error fetching user posts');
      }
    };

    if (userIdToFetch) {
      fetchUserPosts();
    }
  }, [authToken, authTokenType, userIdToFetch]);

  // Construct the image URL based on `image_url_type`
  const getImageUrl = (post) => {
    return post.image_url_type === 'absolute' ? post.image_url : `${BASE_URL}${post.image_url}`;
  };

  if (!userProfile) return <div>Loading...</div>;

  return (
    <div className="profile">
      <div className="profile_header">
        <div className="profile_avatar">
          <img
            src={userProfile.avatar ? getImageUrl(userProfile) : DefaultProfilePic}
            alt="Profile Avatar"
          />
        </div>
        <div className="profile_info">
          <h1>{userProfile.username}</h1>
          <div className="profile_counts">
            <span>{userPosts.length} публикаций</span>
            <span>{userProfile.followers_count || 0} подписчиков</span>
            <span>{userProfile.following_count || 0} подписок</span>
          </div>
        </div>
      </div>

      <div className="profile_buttons">
        <button className="profile_button">Редактировать профиль</button>
        <button className="profile_button">Посмотреть архив</button>
      </div>

      <div className="profile_tabs">
        <span className="active">ПУБЛИКАЦИИ</span>
        <span>СОХРАНЕННОЕ</span>
        <span>ОТМЕТКИ</span>
      </div>

      <div className="profile_posts">
        {userPosts.length > 0 ? (
          userPosts.map((post) => (
            <div key={post.id} className="profile_post">
              <img src={getImageUrl(post)} alt={post.caption || 'Post'} />
            </div>
          ))
        ) : (
          <div className="no_posts_placeholder">
            <div className="placeholder_icon">📷</div>
            <h2>Поделиться фото</h2>
            <p>Фото, которыми вы делитесь, будут показываться в вашем профиле.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;