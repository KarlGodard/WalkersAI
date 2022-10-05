import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
  */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: '',
      owner: '',
      comments: [],
      likes: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: '',
      timestamp: '',
      commentValue: '',
    };
    this.addComment = this.addComment.bind(this);
    this.handleCommentChange = this.handleCommentChange.bind(this);
    this.deleteComment = this.deleteComment.bind(this);
    this.doubleClick = this.doubleClick.bind(this);
    this.likeAction = this.likeAction.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // console.log(url);
    // console.log('COMPONENT MOUNTED');

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // console.log('Data fetched');
        // console.log(data);
        this.setState({
          imgUrl: data.imgUrl,
          owner: data.owner,
          comments: data.comments,
          likes: data.likes,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
          timestamp: moment.utc(data.created).fromNow(),
        });
      })
      .catch((error) => console.log(error));
  }

  handleCommentChange(event) {
    this.setState({ commentValue: event.target.value });
  }

  likeAction() {
    const {
      postid,
      likes,
    } = this.state;
    // console.log("like btn pressed");
    if (likes.lognameLikesThis) {
      // const likeUrl = '/api/v1/likes/'.concat(like_info.likeid, '/');
      const likeUrl = likes.url;
      fetch(likeUrl, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response;
        })
        .then(() => {
          this.setState((prevState) => ({
            likes: {
              lognameLikesThis: false,
              numLikes: prevState.likes.numLikes - 1,
              url: null,
            },
          }));
        }).catch((error) => console.log(error));
    } else { // add like
      const likeUrl = '/api/v1/likes/?postid='.concat(postid);
      fetch(likeUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState((prevState) => ({
            likes: {
              lognameLikesThis: true,
              numLikes: prevState.likes.numLikes + 1,
              url: '/api/v1/likes/'.concat(data.likeid, '/'),
            },
          }));
        }).catch((error) => console.log(error));
    }
  }

  addComment(event) {
    const {
      postid,
      comments,
    } = this.state;

    event.preventDefault();

    const commentUrl = '/api/v1/comments/?postid='.concat(postid);
    fetch(commentUrl, {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: event.target.value }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: comments.concat({
            commentid: data.commentid,
            lognameOwnsThis: data.lognameOwnsThis,
            owner: data.owner,
            ownerShowUrl: data.ownerShowUrl,
            text: data.text,
            url: data.url,
          }),
          commentValue: '',
        });
      }).catch((error) => console.log(error));
  }

  doubleClick() { // only adds like if logname doesnt like
    const {
      postid,
      likes,
    } = this.state;
    if (!likes.lognameLikesThis) { // add like
      const likeUrl = '/api/v1/likes/?postid='.concat(postid);
      fetch(likeUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState((prevState) => ({
            likes: {
              lognameLikesThis: true,
              numLikes: prevState.likes.numLikes + 1,
              url: '/api/v1/likes/'.concat(data.likeid, '/'),
            },
          }));
        }).catch((error) => console.log(error));
    }
  }

  deleteComment(event) {
    let commentid = event.target.value;

    const url = '/api/v1/comments/'.concat(commentid, '/');
    fetch(url, { credentials: 'same-origin', method: 'DELETE' })
      .then((response) => {
        if (response.status !== 204 && !response.ok) throw Error(response.statusText);
        // Change commentid to an int so we can use it to find which comment to delete
        commentid = parseInt(commentid, 10);

        this.setState((prevState) => ({
          comments: prevState.comments.filter((comment) => comment.commentid !== commentid),
        }));
        // return response.json();
      }).catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      imgUrl, owner, comments,
      likes, ownerImgUrl,
      ownerShowUrl, postShowUrl,
      postid, timestamp,
      commentValue,
    } = this.state;

    const handleKeypress = (e) => {
      if (e.code === 'Enter') {
        this.addComment(e);
      }
    };
    const commentList = comments.map((comment) => (
      <p key={comment.commentid}>
        <a
          href={comment.ownerShowUrl}
        >
          {comment.owner}
        </a>
        &nbsp;
        {comment.text}
        &nbsp;

        {comment.lognameOwnsThis && (
          <button type="submit" value={comment.commentid} className="delete-comment-button" onClick={this.deleteComment}>
            Delete comment
          </button>
        )}
      </p>
    ));

    return (
      <div key={postid} className="post">
        <div style={{ float: 'left' }}>
          <a href={ownerShowUrl}>
            <img
              src={ownerImgUrl}
              alt="profile pic"
              style={{ width: '40px', height: '50px' }}
            />
          </a>
          <a href={ownerShowUrl}>{owner}</a>
        </div>
        <div style={{ float: 'right' }}>
          <a href={postShowUrl}>{timestamp}</a>
        </div>
        <div onDoubleClick={this.doubleClick}>
          <img
            src={imgUrl}
            alt=""
            style={{ width: '300px', height: '300px' }}
            className="center"
          />
        </div>
        <strong>
          {likes.numLikes}
          {likes.numLikes === 1 ? ' like' : ' likes'}
        </strong>
        <br />
        <button className="like-unlike-button" onClick={this.likeAction} type="button">
          {likes.lognameLikesThis ? 'unlike' : 'like'}
        </button>
        <br />
        {commentList}
        <form onSubmit={this.addComment} className="comment-form">
          <input
            type="text"
            value={commentValue}
            onKeyPress={handleKeypress}
            onChange={this.handleCommentChange}
          />
        </form>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;

/*
<button className='like-unlike-button' onClick={this.likeAction()}>
  {lognameLikesThis ? 'unlike' : 'like'}
</button>
*/
