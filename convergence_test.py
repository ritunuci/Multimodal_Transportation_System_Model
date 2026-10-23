from colorama import Fore, Style
def convergence_test(M_share,M_share_pre):
    diff=abs(M_share-M_share_pre)
    per_diff=diff/M_share_pre
    if per_diff<=0.01:
        converged=True

    return converged,per_diff

def indiv_convergence_test(agent_choice_prob,agent_choice_prob_pre,convergence_gap):
    sum_abs_per_diff=0
    sum_sq_per_diff=0
    sum_sq_diff = 0
    sum_prob=0
    converged=False
    # print(f"{Fore.GREEN}Max agent id is: {max(agent_choice_prob.keys())} and min id is: {min(agent_choice_prob.keys())}{Style.RESET_ALL}")
    for request_id in agent_choice_prob.keys():
        num_modes=len(agent_choice_prob[request_id])
        for i in range(num_modes):
            if agent_choice_prob_pre[request_id][i]==0:
                mode_abs_per_diff=0
            else:
                mode_abs_per_diff=abs(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i])/agent_choice_prob_pre[request_id][i]
            sum_abs_per_diff+=mode_abs_per_diff

            if agent_choice_prob_pre[request_id][i]==0:
                mode_sq_per_diff=0
            else:
                mode_sq_per_diff=(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i])**2/agent_choice_prob_pre[request_id][i]
            sum_sq_per_diff+=mode_sq_per_diff

            mode_sq_diff=(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i]) ** 2
            sum_sq_diff += mode_sq_diff
            #
            sum_prob+=agent_choice_prob_pre[request_id][i]


    per_sq_diff=sum_sq_diff/sum_prob
    # per_abs_diff = sum_abs_diff / sum_prob
    if sum_sq_per_diff<=convergence_gap:
        converged=True

    print("converged:",converged,"sum_abs_per_diff:",sum_abs_per_diff,"sum_sq_per_diff",sum_sq_per_diff,"per_sq_diff",per_sq_diff)

    return converged,sum_sq_per_diff


# def indiv_convergence_test_binary_choice(agent_choice_prob,agent_choice_prob_pre):
#     sum_abs_per_diff=0
#     sum_sq_per_diff=0
#     sum_sq_diff = 0
#     sum_prob=0
#     converged=False
#     for request_id in agent_choice_prob.keys():
#         for i in range(2):
#             if agent_choice_prob_pre[request_id][i]==0:
#                 mode_abs_per_diff=0
#             else:
#                 mode_abs_per_diff=abs(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i])/agent_choice_prob_pre[request_id][i]
#             sum_abs_per_diff+=mode_abs_per_diff
#
#             if agent_choice_prob_pre[request_id][i]==0:
#                 mode_sq_per_diff=0
#             else:
#                 mode_sq_per_diff=(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i])**2/agent_choice_prob_pre[request_id][i]
#             sum_sq_per_diff+=mode_sq_per_diff
#
#             mode_sq_diff=(agent_choice_prob[request_id][i] - agent_choice_prob_pre[request_id][i]) ** 2
#             sum_sq_diff += mode_sq_diff
#             #
#             sum_prob+=agent_choice_prob_pre[request_id][i]
#
#         # M_diff=abs(agent_choice_prob[request_id][0]-agent_choice_prob_pre[request_id][0])
#         # D_diff = abs(agent_choice_prob[request_id][1] - agent_choice_prob_pre[request_id][1])
#         # F_diff = abs(agent_choice_prob[request_id][2] - agent_choice_prob_pre[request_id][2])
#         #
#         # M_sq_diff = (agent_choice_prob[request_id][0]-agent_choice_prob_pre[request_id][0])**2
#         # D_sq_diff = (agent_choice_prob[request_id][1] - agent_choice_prob_pre[request_id][1])**2
#         # F_sq_diff = (agent_choice_prob[request_id][2] - agent_choice_prob_pre[request_id][2])**2
#         # sum_diff=
#         #
#         # pre_M_prob = agent_choice_prob_pre[request_id][0]
#         # pre_D_prob = agent_choice_prob_pre[request_id][1]
#         # pre_F_prob = agent_choice_prob_pre[request_id][2]
#
#
#     per_sq_diff=sum_sq_diff/sum_prob
#     # per_abs_diff = sum_abs_diff / sum_prob
#     if sum_sq_per_diff<=0.001:
#         converged=True
#
#     print("converged:",converged,"sum_abs_per_diff:",sum_abs_per_diff,"sum_sq_per_diff",sum_sq_per_diff,"per_sq_diff",per_sq_diff)
#
#     return converged,sum_sq_per_diff