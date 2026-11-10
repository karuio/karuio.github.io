/** xnews — static news reader (assets only). */
export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  },
};
