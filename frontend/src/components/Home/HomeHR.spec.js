import React from "react";
import { shallow } from "enzyme";
import HomeHR from "./HomeHR";
import { configure } from "enzyme";
import Adapter from "enzyme-adapter-react-16";

configure({ adapter: new Adapter() });

describe("HomeHR", () => {
  let wrapper;
  beforeEach(() => (wrapper = shallow(<HomeHR />)));
  it("Home HR page should exist", () => {
    expect(wrapper.exists()).toBe(true);
  });
  it("should have container", () => {
    expect(wrapper.find("Container").length).toEqual(1);
  });
  it("should have h1", () => {
    expect(wrapper.find("h1").length).toEqual(1);
  });
  it("should have h4", () => {
    expect(wrapper.find("h4").length).toEqual(1);
  });
  it("should have h5", () => {
    expect(wrapper.find("h5").length).toEqual(1);
  });
});
