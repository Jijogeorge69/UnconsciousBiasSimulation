import React, { Component } from "react";
import { Container, Card, Accordion, Modal, Button } from "react-bootstrap";
import Header from "../Header/Header";
import Profile from "../viewProfile/Profile";
import ls from "local-storage";

class ViewProfiles extends Component {
  constructor() {
    super();
    this.state = {
      profiles: [],
      modal_show: false,
      modal_message: ""
    };
  }

  modalHide = () => {
    this.setState({ modal_show: false })
  }
  modalShow = (message) => {
    this.setState({ modal_show: true })
    this.setState({ modal_message: message })
  }

  componentDidMount() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userId = urlParams.get('userId')
    const token = ls.get("token");
    console.log(token)
    fetch("http://localhost:5000/api/v1/getProfiles/" + userId + "/",
      {
        headers: {
          "Authorization": "Bearer " + token
        }
      })
      .then((response) => response.json())
      .then((res) => {

        if (res["results"].error !== 'Profiles not found') {
          this.setState({ profiles: res["results"] });
        }
        else {
          this.modalShow(res["results"].error)
        }
      });
  }

  render() {
    return (
      <>
        <Header />
        <Container className="justify-content-center">
          <Accordion defaultActiveKey="0">
            {this.state.profiles.map((profile, i) => (
              <Card>
                <Accordion.Toggle as={Card.Header} eventKey={i + 1}>
                  {profile.profileName}
                </Accordion.Toggle>
                <Accordion.Collapse eventKey={i + 1}>
                  <Card.Body>
                    <Profile profile={profile} />
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
            ))}
          </Accordion>
        </Container>

        <Modal show={this.state.modal_show} onHide={this.modalHide} backdrop="static"
          keyboard={false}>
          <Modal.Body>{this.state.modal_message}</Modal.Body>
          <Modal.Footer>
            <Button variant="primary" onClick={this.modalHide}>
              Continue
          </Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }
}

export default ViewProfiles;
