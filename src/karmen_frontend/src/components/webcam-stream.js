import React from 'react';

export class WebcamStream extends React.Component {
  state = {
    isOnline: false,
    isMaximized: false,
  }

  constructor(props) {
    super(props);
    this.testStream = this.testStream.bind(this);
  }

  testStream() {
    const { stream, proxied } = this.props;
    if (!stream && !proxied) {
      this.setState({
        isOnline: false,
      });
      return;
    }
    fetch(stream)
      .then((r) => {
        if (r.status === 200) {
          this.setState({
            isOnline: true,
            source: stream,
          });
        }
      }).catch((e) => {
        fetch(proxied)
          .then((r) => {
            if (r.status === 200) {
              this.setState({
                isOnline: true,
                source: proxied,
              });
            }
          }).catch((e) => {
            // pass
          });
      });
  }

  componentDidMount() {
    this.testStream();
  }

  componentDidUpdate(prevProps) {
    const { stream, proxied } = this.props;
    if (prevProps.stream !== stream || prevProps.proxied !== proxied) {
      this.testStream();
    }
  }

  componentWillUnmount() {
    this.setState({
      isOnline: false,
      source: null,
    })
  }

  render() {
    const { flipHorizontal, flipVertical, rotate90 } = this.props;
    const { isOnline, isMaximized, source } = this.state;
    let klass = [];
    if (flipHorizontal) {
      klass.push('flip-horizontal');
    }

    if (flipVertical) {
      klass.push('flip-vertical');
    }

    if (rotate90) {
      klass.push('rotate-90');
    }

    return <div
      className={`webcam-stream ${isMaximized ? 'maximized' : ''}`}
       onClick={() => {
        const { isMaximized } = this.state;
        this.setState({
          isMaximized: !isMaximized
        })
      }}
    >
      {isOnline ?
        <img
          className={klass.join(' ')}
          alt={source}
          src={`${source}?t=${(new Date()).getTime()}`}
        /> :
        <p className="no-stream">
          Stream unavailable
        </p>
      }
    </div>;
  }
}